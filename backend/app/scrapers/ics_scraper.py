"""
ICS/iCal scraper for calendar-based activity sources.
"""
import logging
from datetime import datetime
from typing import Any

import httpx
from icalendar import Calendar
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider import Provider
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class ICScraper(BaseScraper):
    """
    Scraper for ICS/iCalendar feeds.

    Supports:
    - Single events
    - Recurring events (RRULE)
    - Event metadata (location, description, organizer)
    """

    def __init__(self, db: AsyncSession, provider: Provider):
        """Initialize ICS scraper."""
        super().__init__(db, provider, scraper_type="ics")

    async def fetch_data(self) -> str:
        """
        Fetch ICS feed from provider's data source URL.

        Returns:
            Raw ICS calendar data as string

        Raises:
            httpx.HTTPError: If fetch fails
        """
        if not self.provider.data_source_url:
            raise ValueError(f"Provider {self.provider.name} has no data_source_url")

        logger.info(f"Fetching ICS feed from {self.provider.data_source_url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.provider.data_source_url)
            response.raise_for_status()
            return response.text

    async def parse_data(self, raw_data: str) -> list[dict[str, Any]]:
        """
        Parse ICS calendar data into activity records.

        Args:
            raw_data: Raw ICS calendar data

        Returns:
            List of activity dictionaries
        """
        activities = []

        try:
            # Parse ICS calendar
            calendar = Calendar.from_ical(raw_data)

            # Extract events
            for component in calendar.walk("VEVENT"):
                try:
                    activity = self._parse_event(component)
                    if activity:
                        activities.append(activity)
                except Exception as e:
                    logger.warning(f"Failed to parse event: {str(e)}")
                    self.warnings.append(f"Event parse error: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to parse ICS calendar: {str(e)}")
            self.errors.append(f"ICS parse error: {str(e)}")

        return activities

    def _parse_event(self, event: Any) -> dict[str, Any] | None:
        """
        Parse individual VEVENT into activity dictionary.

        Args:
            event: iCalendar VEVENT component

        Returns:
            Activity dictionary or None if invalid
        """
        # Extract basic fields
        name = str(event.get("SUMMARY", ""))
        if not name:
            return None

        description = str(event.get("DESCRIPTION", "")) if event.get("DESCRIPTION") else None

        # Extract dates
        dtstart = event.get("DTSTART")
        dtend = event.get("DTEND")

        start_date = None
        start_time = None
        end_time = None

        if dtstart:
            if hasattr(dtstart.dt, "date"):
                start_date = dtstart.dt.date()
                if hasattr(dtstart.dt, "time"):
                    start_time = dtstart.dt.time()
            else:
                start_date = dtstart.dt

        if dtend:
            if hasattr(dtend.dt, "time"):
                end_time = dtend.dt.time()

        # Extract RRULE for recurring events
        rrule = None
        if event.get("RRULE"):
            rrule = str(event.get("RRULE").to_ical().decode())

        # Extract location
        location = str(event.get("LOCATION", "")) if event.get("LOCATION") else None

        # Extract organizer
        organizer = str(event.get("ORGANIZER", "")) if event.get("ORGANIZER") else None

        # Extract URL
        url = str(event.get("URL", "")) if event.get("URL") else None

        # Build activity dictionary
        activity = {
            "name": name,
            "description": description,
            "start_date": start_date,
            "start_time": start_time,
            "end_time": end_time,
            "rrule": rrule,
            "source_url": url or self.provider.data_source_url,
            "last_verified": datetime.now().date(),
        }

        # TODO: Parse location into venue (geocoding)
        # TODO: Extract age ranges from description
        # TODO: Extract pricing from description
        # TODO: Extract activity type from categories

        return activity
