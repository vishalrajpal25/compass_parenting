"""
JSON scraper for API-based activity sources.

Supports:
- REST APIs (Eventbrite, city open data portals)
- JSON feeds
- Structured JSON responses
"""
import json
import logging
from datetime import datetime
from typing import Any, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider import Provider
from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class JSONScraper(BaseScraper):
    """
    Scraper for JSON-based data sources.
    
    Supports:
    - REST APIs with pagination
    - JSON feeds
    - Open data portal APIs
    """

    def __init__(
        self,
        db: AsyncSession,
        provider: Provider,
        json_path: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize JSON scraper.

        Args:
            db: Database session
            provider: Provider being scraped
            json_path: Optional JSONPath to extract events array (e.g., "events", "data.items")
            api_key: Optional API key for authenticated endpoints
        """
        super().__init__(db, provider, scraper_type="json")
        self.json_path = json_path
        self.api_key = api_key

    async def fetch_data(self) -> dict[str, Any]:
        """
        Fetch JSON data from provider's data source URL.

        Returns:
            Parsed JSON data as dictionary

        Raises:
            httpx.HTTPError: If fetch fails
            json.JSONDecodeError: If JSON parsing fails
        """
        if not self.provider.data_source_url:
            raise ValueError(f"Provider {self.provider.name} has no data_source_url")

        logger.info(f"Fetching JSON from {self.provider.data_source_url}")

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            # Some APIs use different auth headers
            headers["X-API-Key"] = self.api_key

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.provider.data_source_url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def parse_data(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Parse JSON data into activity records.

        Args:
            raw_data: Parsed JSON data

        Returns:
            List of activity dictionaries
        """
        activities = []

        try:
            # Extract events array using json_path if specified
            events_data = raw_data
            if self.json_path:
                # Simple path traversal (e.g., "events", "data.items")
                parts = self.json_path.split(".")
                for part in parts:
                    if isinstance(events_data, dict):
                        events_data = events_data.get(part)
                    elif isinstance(events_data, list):
                        # If we hit a list, use it
                        break
                    else:
                        logger.warning(f"JSON path '{self.json_path}' not found in response")
                        return []

            # Ensure we have a list
            if not isinstance(events_data, list):
                if isinstance(events_data, dict):
                    # Single event or wrapped in object
                    events_data = [events_data]
                else:
                    logger.warning(f"Expected list or dict, got {type(events_data)}")
                    return []

            # Parse each event
            for event_data in events_data:
                try:
                    activity = self._parse_event(event_data)
                    if activity:
                        activities.append(activity)
                except Exception as e:
                    logger.warning(f"Failed to parse event: {str(e)}")
                    self.warnings.append(f"Event parse error: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            self.errors.append(f"JSON parse error: {str(e)}")

        return activities

    def _parse_event(self, event_data: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Parse individual event object into activity dictionary.

        Handles common API formats:
        - Eventbrite format
        - Generic event APIs
        - Open data portal formats

        Args:
            event_data: Event object from JSON

        Returns:
            Activity dictionary or None if invalid
        """
        # Try to extract name (common field names)
        name = (
            event_data.get("name") or
            event_data.get("title") or
            event_data.get("event_name") or
            event_data.get("summary") or
            ""
        )

        if not name:
            return None

        # Extract description
        description = (
            event_data.get("description") or
            event_data.get("summary") or
            event_data.get("details") or
            event_data.get("text") or
            None
        )

        # Extract dates (handle various formats)
        start_date = None
        start_time = None
        end_time = None

        # Try different date field names
        start_str = (
            event_data.get("start") or
            event_data.get("start_date") or
            event_data.get("start_time") or
            event_data.get("date") or
            event_data.get("datetime_start")
        )

        if start_str:
            # Parse ISO format or common date formats
            try:
                if isinstance(start_str, str):
                    # Try ISO format
                    if "T" in start_str:
                        dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                        start_date = dt.date()
                        start_time = dt.time()
                    else:
                        # Just date
                        start_date = datetime.fromisoformat(start_str).date()
                elif isinstance(start_str, dict):
                    # Nested date object (e.g., {"local": "2024-01-01T10:00:00"})
                    local_str = start_str.get("local") or start_str.get("utc")
                    if local_str:
                        dt = datetime.fromisoformat(local_str.replace("Z", "+00:00"))
                        start_date = dt.date()
                        start_time = dt.time()
            except (ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse start date: {start_str}, error: {str(e)}")

        # Extract end time
        end_str = (
            event_data.get("end") or
            event_data.get("end_date") or
            event_data.get("end_time") or
            event_data.get("datetime_end")
        )

        if end_str:
            try:
                if isinstance(end_str, str):
                    if "T" in end_str:
                        dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                        end_time = dt.time()
            except (ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse end time: {end_str}, error: {str(e)}")

        # Extract location/venue
        venue = None
        location_data = (
            event_data.get("venue") or
            event_data.get("location") or
            event_data.get("place") or
            {}
        )

        if location_data:
            if isinstance(location_data, dict):
                venue = {
                    "name": location_data.get("name") or location_data.get("venue_name"),
                    "address": location_data.get("address") or location_data.get("address_1"),
                    "city": location_data.get("city"),
                    "state": location_data.get("state") or location_data.get("region"),
                    "zip_code": location_data.get("zip_code") or location_data.get("postal_code"),
                }
            elif isinstance(location_data, str):
                venue = {"name": location_data, "address": location_data}

        # Extract URL
        url = (
            event_data.get("url") or
            event_data.get("event_url") or
            event_data.get("link") or
            event_data.get("website") or
            self.provider.data_source_url
        )

        # Extract price (handle various formats)
        price_cents = None
        price_text = None

        price_data = event_data.get("price") or event_data.get("cost") or event_data.get("ticket_price")
        if price_data:
            if isinstance(price_data, (int, float)):
                price_cents = int(price_data * 100) if price_data > 0 else None
            elif isinstance(price_data, dict):
                # Eventbrite format: {"currency": "USD", "value": 25.00}
                value = price_data.get("value") or price_data.get("amount")
                if value:
                    price_cents = int(float(value) * 100) if float(value) > 0 else None
            elif isinstance(price_data, str):
                price_text = price_data
                # Try to extract number
                import re
                match = re.search(r'[\d.]+', price_text)
                if match:
                    try:
                        price_cents = int(float(match.group()) * 100)
                    except ValueError:
                        pass

        # Extract age range (if available)
        min_age = event_data.get("min_age") or event_data.get("age_min")
        max_age = event_data.get("max_age") or event_data.get("age_max")
        age_range_text = event_data.get("age_range") or event_data.get("ages")

        # Build activity dictionary
        activity = {
            "name": name,
            "description": description,
            "start_date": start_date,
            "start_time": start_time,
            "end_time": end_time,
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

