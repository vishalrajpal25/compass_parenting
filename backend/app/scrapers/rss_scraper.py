"""
RSS/Atom feed scraper for activity sources.
"""
import logging
from datetime import datetime
from typing import Any

import feedparser
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider import Provider
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class RSSScraper(BaseScraper):
    """
    Scraper for RSS/Atom feeds.

    Extracts activity information from blog posts, event feeds, etc.
    """

    def __init__(self, db: AsyncSession, provider: Provider):
        """Initialize RSS scraper."""
        super().__init__(db, provider, scraper_type="rss")

    async def fetch_data(self) -> str:
        """
        Fetch RSS/Atom feed from provider's data source URL.

        Returns:
            Raw feed data as string

        Raises:
            httpx.HTTPError: If fetch fails
        """
        if not self.provider.data_source_url:
            raise ValueError(f"Provider {self.provider.name} has no data_source_url")

        logger.info(f"Fetching RSS feed from {self.provider.data_source_url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.provider.data_source_url)
            response.raise_for_status()
            return response.text

    async def parse_data(self, raw_data: str) -> list[dict[str, Any]]:
        """
        Parse RSS/Atom feed into activity records.

        Args:
            raw_data: Raw feed data

        Returns:
            List of activity dictionaries
        """
        activities = []

        try:
            # Parse feed
            feed = feedparser.parse(raw_data)

            # Extract entries
            for entry in feed.entries:
                try:
                    activity = self._parse_entry(entry)
                    if activity:
                        activities.append(activity)
                except Exception as e:
                    logger.warning(f"Failed to parse entry: {str(e)}")
                    self.warnings.append(f"Entry parse error: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to parse RSS feed: {str(e)}")
            self.errors.append(f"RSS parse error: {str(e)}")

        return activities

    def _parse_entry(self, entry: Any) -> dict[str, Any] | None:
        """
        Parse individual feed entry into activity dictionary.

        Args:
            entry: feedparser entry

        Returns:
            Activity dictionary or None if invalid
        """
        # Extract basic fields
        name = entry.get("title", "")
        if not name:
            return None

        description = entry.get("summary", "") or entry.get("description", "")

        # Extract link
        link = entry.get("link", "")

        # Extract published date
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        start_date = None
        if published:
            start_date = datetime(*published[:3]).date()

        # Build activity dictionary
        activity = {
            "name": name,
            "description": description,
            "start_date": start_date,
            "source_url": link or self.provider.data_source_url,
            "last_verified": datetime.now().date(),
        }

        # TODO: Parse content for event details (dates, times, location, pricing)
        # TODO: Extract structured data if available
        # TODO: Use LLM to extract key fields from description (optional)

        return activity
