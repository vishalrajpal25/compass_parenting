"""
CSV scraper for CSV-based activity sources.

Supports:
- City open data portal CSV downloads
- CSV exports from recreation systems
- Structured CSV files
"""
import csv
import io
import logging
from datetime import datetime
from typing import Any, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider import Provider
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class CSVScraper(BaseScraper):
    """
    Scraper for CSV-based data sources.
    
    Supports:
    - CSV files from URLs
    - Open data portal CSV exports
    - Recreation department CSV downloads
    """

    def __init__(
        self,
        db: AsyncSession,
        provider: Provider,
        encoding: str = "utf-8",
        delimiter: str = ",",
    ):
        """
        Initialize CSV scraper.

        Args:
            db: Database session
            provider: Provider being scraped
            encoding: CSV file encoding (default: utf-8)
            delimiter: CSV delimiter (default: comma)
        """
        super().__init__(db, provider, scraper_type="csv")
        self.encoding = encoding
        self.delimiter = delimiter

    async def fetch_data(self) -> str:
        """
        Fetch CSV data from provider's data source URL.

        Returns:
            Raw CSV data as string

        Raises:
            httpx.HTTPError: If fetch fails
        """
        if not self.provider.data_source_url:
            raise ValueError(f"Provider {self.provider.name} has no data_source_url")

        logger.info(f"Fetching CSV from {self.provider.data_source_url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.provider.data_source_url)
            response.raise_for_status()
            # Try to decode with specified encoding
            try:
                return response.text
            except UnicodeDecodeError:
                # Fallback to latin-1 if utf-8 fails
                return response.content.decode("latin-1")

    async def parse_data(self, raw_data: str) -> list[dict[str, Any]]:
        """
        Parse CSV data into activity records.

        Args:
            raw_data: Raw CSV data as string

        Returns:
            List of activity dictionaries
        """
        activities = []

        try:
            # Parse CSV
            csv_reader = csv.DictReader(
                io.StringIO(raw_data),
                delimiter=self.delimiter
            )

            # Extract rows
            for row in csv_reader:
                try:
                    activity = self._parse_row(row)
                    if activity:
                        activities.append(activity)
                except Exception as e:
                    logger.warning(f"Failed to parse row: {str(e)}")
                    self.warnings.append(f"Row parse error: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to parse CSV: {str(e)}")
            self.errors.append(f"CSV parse error: {str(e)}")

        return activities

    def _parse_row(self, row_data: dict[str, str]) -> Optional[dict[str, Any]]:
        """
        Parse CSV row into activity dictionary.

        Handles common CSV formats:
        - City recreation department exports
        - Open data portal formats
        - Generic event CSVs

        Args:
            row_data: Dictionary mapping column names to values

        Returns:
            Activity dictionary or None if invalid
        """
        # Normalize column names (case-insensitive, strip whitespace)
        normalized_row = {k.strip().lower(): v.strip() if v else "" for k, v in row_data.items()}

        # Extract name (common column names)
        name = (
            normalized_row.get("name") or
            normalized_row.get("title") or
            normalized_row.get("activity") or
            normalized_row.get("program") or
            normalized_row.get("event_name") or
            ""
        )

        if not name:
            return None

        # Extract description
        description = (
            normalized_row.get("description") or
            normalized_row.get("details") or
            normalized_row.get("summary") or
            None
        )

        # Extract dates (handle various formats)
        start_date = None
        start_time = None

        start_str = (
            normalized_row.get("start_date") or
            normalized_row.get("date") or
            normalized_row.get("start") or
            normalized_row.get("event_date") or
            normalized_row.get("begin_date")
        )

        if start_str:
            try:
                # Try common date formats
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M"]:
                    try:
                        dt = datetime.strptime(start_str, fmt)
                        start_date = dt.date()
                        if "%H" in fmt:
                            start_time = dt.time()
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.warning(f"Failed to parse date: {start_str}, error: {str(e)}")

        # Extract location/venue
        venue = None
        venue_name = (
            normalized_row.get("venue") or
            normalized_row.get("location") or
            normalized_row.get("facility") or
            normalized_row.get("place")
        )

        address = normalized_row.get("address") or normalized_row.get("street_address")
        city = normalized_row.get("city")
        state = normalized_row.get("state")
        zip_code = normalized_row.get("zip") or normalized_row.get("zip_code") or normalized_row.get("postal_code")

        if venue_name or address:
            venue = {
                "name": venue_name,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
            }

        # Extract price
        price_cents = None
        price_text = (
            normalized_row.get("price") or
            normalized_row.get("cost") or
            normalized_row.get("fee") or
            normalized_row.get("registration_fee")
        )

        if price_text:
            # Try to extract number
            import re
            match = re.search(r'[\d.]+', price_text)
            if match:
                try:
                    price_cents = int(float(match.group()) * 100)
                except ValueError:
                    pass

        # Extract age range
        min_age = None
        max_age = None
        age_range_text = (
            normalized_row.get("age") or
            normalized_row.get("ages") or
            normalized_row.get("age_range") or
            normalized_row.get("age_group")
        )

        if age_range_text:
            # Try to parse "5-12" or "5 to 12" format
            import re
            match = re.search(r'(\d+)[\s-]+(?:to|-)?[\s-]*(\d+)', age_range_text)
            if match:
                try:
                    min_age = int(match.group(1))
                    max_age = int(match.group(2))
                except ValueError:
                    pass
            else:
                # Try single age
                match = re.search(r'(\d+)', age_range_text)
                if match:
                    try:
                        min_age = int(match.group(1))
                    except ValueError:
                        pass

        # Also check explicit min/max columns
        if not min_age:
            min_age_str = normalized_row.get("min_age") or normalized_row.get("age_min")
            if min_age_str:
                try:
                    min_age = int(min_age_str)
                except ValueError:
                    pass

        if not max_age:
            max_age_str = normalized_row.get("max_age") or normalized_row.get("age_max")
            if max_age_str:
                try:
                    max_age = int(max_age_str)
                except ValueError:
                    pass

        # Extract URL
        url = (
            normalized_row.get("url") or
            normalized_row.get("link") or
            normalized_row.get("registration_url") or
            normalized_row.get("website") or
            self.provider.data_source_url
        )

        # Build activity dictionary
        activity = {
            "name": name,
            "description": description,
            "start_date": start_date,
            "start_time": start_time,
            "price_cents": price_cents,
            "price_text": price_text,
            "min_age": min_age,
            "max_age": max_age,
            "age_range_text": age_range_text,
            "source_url": url,
            "last_verified": datetime.now().date(),
            "venue": venue,
        }

        return activity

