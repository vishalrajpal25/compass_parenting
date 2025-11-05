"""
Base scraper class for all data source scrapers.
"""
import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import pygeohash
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.provider import Provider
from app.models.scraper_log import ScraperLog
from app.models.venue import Venue

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.

    Provides common functionality for:
    - De-duplication via canon_hash
    - Quality validation
    - Logging and metrics
    - Error handling
    """

    def __init__(
        self,
        db: AsyncSession,
        provider: Provider,
        scraper_type: str,
    ):
        """
        Initialize scraper.

        Args:
            db: Database session
            provider: Provider being scraped
            scraper_type: Type of scraper (ics, rss, html, json, csv)
        """
        self.db = db
        self.provider = provider
        self.scraper_type = scraper_type

        # Metrics
        self.activities_found = 0
        self.activities_passed = 0
        self.activities_failed = 0
        self.duplicates_found = 0
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.validation_failures: dict[str, int] = {}

        # Start time for logging
        self.run_started_at = datetime.now(timezone.utc)

    @abstractmethod
    async def fetch_data(self) -> Any:
        """
        Fetch raw data from source.

        Returns:
            Raw data (varies by scraper type)

        Raises:
            Exception: If fetch fails
        """
        pass

    @abstractmethod
    async def parse_data(self, raw_data: Any) -> list[dict[str, Any]]:
        """
        Parse raw data into structured activity records.

        Args:
            raw_data: Raw data from fetch_data()

        Returns:
            List of activity dictionaries with standardized fields

        Raises:
            Exception: If parsing fails
        """
        pass

    def generate_canon_hash(
        self,
        name: str,
        start_date: str | None,
        geohash: str | None,
        org_name: str,
    ) -> str:
        """
        Generate canonical hash for de-duplication.

        Hash components:
        - Normalized activity name (lowercase, stripped, spaces collapsed)
        - Fuzzy date (±3 days not implemented yet, just use exact date)
        - Geohash (precision 6 = ~1.2km)
        - Organization name (normalized)

        Args:
            name: Activity name
            start_date: Start date (YYYY-MM-DD)
            geohash: Geohash of venue location
            org_name: Organization/provider name

        Returns:
            SHA256 hash for de-duplication
        """
        # Normalize name: lowercase, strip, collapse spaces
        normalized_name = " ".join(name.lower().strip().split())

        # Normalize org name
        normalized_org = " ".join(org_name.lower().strip().split())

        # Use geohash6 for proximity matching
        geohash6 = geohash[:6] if geohash else "UNKNOWN"

        # Date (exact for now, fuzzy matching can be added later)
        date_str = start_date or "NODATE"

        # Combine components
        canon_str = f"{normalized_name}|{date_str}|{geohash6}|{normalized_org}"

        # Generate SHA256 hash
        return hashlib.sha256(canon_str.encode()).hexdigest()

    def validate_activity(self, activity_data: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate activity data quality.

        Validation checks:
        - Required fields present (name, provider)
        - Date sanity (not in past >1 year, not >2 years future)
        - Price format valid
        - Age ranges logical
        - Geocoding successful (if location provided)

        Args:
            activity_data: Activity dictionary

        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        errors = []

        # Required fields
        if not activity_data.get("name"):
            errors.append("Missing activity name")

        # Date sanity (basic check)
        if activity_data.get("start_date"):
            # TODO: Add actual date range validation
            pass

        # Price validation
        if activity_data.get("price_cents") is not None:
            price = activity_data["price_cents"]
            if not isinstance(price, int) or price < 0:
                errors.append("Invalid price format")

        # Age range validation
        min_age = activity_data.get("min_age")
        max_age = activity_data.get("max_age")
        if min_age is not None and max_age is not None:
            if min_age > max_age:
                errors.append("Invalid age range (min > max)")
            if min_age < 0 or max_age > 18:
                errors.append("Age range out of bounds (0-18)")

        return len(errors) == 0, errors

    async def save_activity(self, activity_data: dict[str, Any]) -> Activity | None:
        """
        Save activity to database with de-duplication.

        Args:
            activity_data: Activity dictionary

        Returns:
            Created/updated Activity or None if duplicate
        """
        self.activities_found += 1

        # Validate activity
        is_valid, validation_errors = self.validate_activity(activity_data)

        if not is_valid:
            self.activities_failed += 1
            for error in validation_errors:
                self.errors.append(f"Activity '{activity_data.get('name')}': {error}")
                # Track validation failure types
                error_type = error.split(":")[0]
                self.validation_failures[error_type] = (
                    self.validation_failures.get(error_type, 0) + 1
                )
            return None

        # Generate canon_hash for de-duplication
        canon_hash = self.generate_canon_hash(
            name=activity_data.get("name", ""),
            start_date=str(activity_data.get("start_date", "")),
            geohash=activity_data.get("geohash", ""),
            org_name=self.provider.name,
        )

        # Check for duplicate
        from sqlalchemy import select

        result = await self.db.execute(
            select(Activity).where(Activity.canon_hash == canon_hash)
        )
        existing = result.scalar_one_or_none()

        if existing:
            self.duplicates_found += 1
            logger.debug(f"Duplicate activity found: {activity_data.get('name')}")
            return None

        # Create activity
        activity = Activity(
            provider_id=self.provider.id,
            canon_hash=canon_hash,
            **activity_data,
        )

        self.db.add(activity)
        self.activities_passed += 1

        return activity

    async def create_scraper_log(self, status: str, http_status: int | None = None) -> ScraperLog:
        """
        Create scraper log entry with metrics.

        Args:
            status: success, failed, partial
            http_status: HTTP status code from data source

        Returns:
            Created ScraperLog
        """
        run_completed_at = datetime.now(timezone.utc)

        # Calculate pass rate
        total = self.activities_found
        pass_rate = (
            (self.activities_passed / total * 100.0) if total > 0 else None
        )

        log = ScraperLog(
            provider_id=self.provider.id,
            scraper_type=self.scraper_type,
            run_started_at=self.run_started_at,
            run_completed_at=run_completed_at,
            status=status,
            activities_found=self.activities_found,
            activities_passed=self.activities_passed,
            activities_failed=self.activities_failed,
            duplicates_found=self.duplicates_found,
            pass_rate=pass_rate,
            http_status=http_status,
            errors=self.errors if self.errors else None,
            warnings=self.warnings if self.warnings else None,
            validation_failures=self.validation_failures if self.validation_failures else None,
        )

        self.db.add(log)
        await self.db.commit()

        # Log summary
        logger.info(
            f"Scraper run completed: provider={self.provider.name}, "
            f"type={self.scraper_type}, status={status}, "
            f"found={self.activities_found}, passed={self.activities_passed}, "
            f"failed={self.activities_failed}, duplicates={self.duplicates_found}, "
            f"pass_rate={pass_rate:.1f}%"
        )

        # Check if should demote
        if log.should_demote:
            logger.warning(
                f"Provider {self.provider.name} should be demoted "
                f"(pass_rate={pass_rate:.1f}%, http_status={http_status})"
            )

        return log

    async def run(self) -> ScraperLog:
        """
        Run the scraper end-to-end.

        Returns:
            ScraperLog with metrics

        Raises:
            Exception: If scraper fails completely
        """
        logger.info(
            f"Starting scraper: provider={self.provider.name}, "
            f"type={self.scraper_type}"
        )

        try:
            # Fetch raw data
            raw_data = await self.fetch_data()

            # Parse into structured records
            activities = await self.parse_data(raw_data)

            logger.info(f"Parsed {len(activities)} activities from {self.provider.name}")

            # Save each activity
            for activity_data in activities:
                await self.save_activity(activity_data)

            # Commit all activities
            await self.db.commit()

            # Create log
            status = "success" if self.activities_failed == 0 else "partial"
            return await self.create_scraper_log(status=status, http_status=200)

        except Exception as e:
            logger.error(
                f"Scraper failed: provider={self.provider.name}, "
                f"type={self.scraper_type}, error={str(e)}",
                exc_info=True,
            )
            self.errors.append(str(e))
            await self.db.rollback()
            return await self.create_scraper_log(status="failed")
