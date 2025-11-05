"""
HTML table scraper for structured activity listings.
"""
import logging
from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider import Provider
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class HTMLScraper(BaseScraper):
    """
    Scraper for HTML tables with consistent structure.

    Only scrapes sources with reliable, consistent table structure.
    Requires configuration of CSS selectors or XPath for each provider.
    """

    def __init__(
        self,
        db: AsyncSession,
        provider: Provider,
        table_selector: str = "table",
        header_row: int = 0,
    ):
        """
        Initialize HTML scraper.

        Args:
            db: Database session
            provider: Provider being scraped
            table_selector: CSS selector for table element
            header_row: Row index for headers (0-based)
        """
        super().__init__(db, provider, scraper_type="html")
        self.table_selector = table_selector
        self.header_row = header_row

    async def fetch_data(self) -> str:
        """
        Fetch HTML page from provider's data source URL.

        Returns:
            Raw HTML as string

        Raises:
            httpx.HTTPError: If fetch fails
        """
        if not self.provider.data_source_url:
            raise ValueError(f"Provider {self.provider.name} has no data_source_url")

        logger.info(f"Fetching HTML from {self.provider.data_source_url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.provider.data_source_url)
            response.raise_for_status()
            return response.text

    async def parse_data(self, raw_data: str) -> list[dict[str, Any]]:
        """
        Parse HTML table into activity records.

        Args:
            raw_data: Raw HTML data

        Returns:
            List of activity dictionaries
        """
        activities = []

        try:
            # Parse HTML
            soup = BeautifulSoup(raw_data, "html.parser")

            # Find table
            table = soup.select_one(self.table_selector)
            if not table:
                raise ValueError(f"Table not found with selector: {self.table_selector}")

            # Extract rows
            rows = table.find_all("tr")
            if len(rows) <= self.header_row:
                raise ValueError("Not enough rows in table")

            # Extract headers
            header_row_elem = rows[self.header_row]
            headers = [th.get_text(strip=True).lower() for th in header_row_elem.find_all(["th", "td"])]

            # Extract data rows
            for row in rows[self.header_row + 1:]:
                try:
                    cells = row.find_all("td")
                    if len(cells) != len(headers):
                        continue

                    row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(len(headers))}

                    activity = self._parse_row(row_data, row)
                    if activity:
                        activities.append(activity)

                except Exception as e:
                    logger.warning(f"Failed to parse row: {str(e)}")
                    self.warnings.append(f"Row parse error: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to parse HTML table: {str(e)}")
            self.errors.append(f"HTML parse error: {str(e)}")

        return activities

    def _parse_row(self, row_data: dict[str, str], row_elem: Any) -> dict[str, Any] | None:
        """
        Parse table row into activity dictionary.

        Args:
            row_data: Dictionary mapping headers to cell values
            row_elem: BeautifulSoup row element (for extracting links)

        Returns:
            Activity dictionary or None if invalid
        """
        # Extract name (common column names)
        name = (
            row_data.get("name") or
            row_data.get("activity") or
            row_data.get("program") or
            row_data.get("title") or
            ""
        )

        if not name:
            return None

        # Extract description
        description = row_data.get("description") or row_data.get("details")

        # Extract dates (basic parsing, can be improved)
        start_date = row_data.get("start date") or row_data.get("date")

        # Extract location
        location = row_data.get("location") or row_data.get("venue")

        # Extract age range
        age_range = row_data.get("age") or row_data.get("ages") or row_data.get("age range")

        # Extract price
        price_text = row_data.get("price") or row_data.get("cost") or row_data.get("fee")

        # Extract registration link (look for <a> tags in row)
        registration_url = None
        link = row_elem.find("a")
        if link and link.get("href"):
            registration_url = link["href"]

        # Build activity dictionary
        activity = {
            "name": name,
            "description": description,
            "start_date": start_date,  # TODO: Parse into date object
            "age_range_text": age_range,
            "price_text": price_text,
            "registration_url": registration_url,
            "source_url": self.provider.data_source_url,
            "last_verified": datetime.now().date(),
        }

        # TODO: Parse dates into date objects
        # TODO: Parse age range into min_age/max_age
        # TODO: Parse price into price_cents
        # TODO: Geocode location into venue

        return activity
