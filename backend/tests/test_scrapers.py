"""
Tests for scraper framework and de-duplication.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.provider import Provider
from app.scrapers.base import BaseScraper


class MockScraper(BaseScraper):
    """Mock scraper for testing base functionality."""

    async def fetch_data(self):
        return "mock_data"

    async def parse_data(self, raw_data):
        return [
            {
                "name": "Test Activity",
                "start_date": "2025-01-15",
                "min_age": 5,
                "max_age": 10,
                "price_cents": 5000,
            }
        ]


def test_generate_canon_hash():
    """Test canonical hash generation for de-duplication."""
    # Create mock database session and provider
    db = MagicMock()
    provider = Provider(
        id=1,
        name="City Recreation",
        organization_type="city_rec",
    )

    scraper = MockScraper(db, provider)

    # Test hash generation
    hash1 = scraper.generate_canon_hash(
        name="Soccer Practice",
        start_date="2025-01-15",
        geohash="9q8yy",
        org_name="City Recreation",
    )

    # Same activity should produce same hash
    hash2 = scraper.generate_canon_hash(
        name="Soccer Practice",
        start_date="2025-01-15",
        geohash="9q8yy",
        org_name="City Recreation",
    )

    assert hash1 == hash2

    # Different name should produce different hash
    hash3 = scraper.generate_canon_hash(
        name="Basketball Practice",
        start_date="2025-01-15",
        geohash="9q8yy",
        org_name="City Recreation",
    )

    assert hash1 != hash3

    # Name normalization (case, whitespace) should produce same hash
    hash4 = scraper.generate_canon_hash(
        name="SOCCER   PRACTICE",  # Different case and extra spaces
        start_date="2025-01-15",
        geohash="9q8yy",
        org_name="City Recreation",
    )

    assert hash1 == hash4


def test_validate_activity():
    """Test activity validation."""
    db = MagicMock()
    provider = Provider(
        id=1,
        name="Test Provider",
        organization_type="test",
    )

    scraper = MockScraper(db, provider)

    # Valid activity
    valid_activity = {
        "name": "Swimming Lessons",
        "start_date": "2025-01-15",
        "min_age": 5,
        "max_age": 10,
        "price_cents": 5000,
    }

    is_valid, errors = scraper.validate_activity(valid_activity)
    assert is_valid
    assert len(errors) == 0

    # Missing name
    invalid_activity = {
        "start_date": "2025-01-15",
    }

    is_valid, errors = scraper.validate_activity(invalid_activity)
    assert not is_valid
    assert "Missing activity name" in errors

    # Invalid price
    invalid_activity = {
        "name": "Test",
        "price_cents": -100,
    }

    is_valid, errors = scraper.validate_activity(invalid_activity)
    assert not is_valid
    assert "Invalid price format" in errors

    # Invalid age range
    invalid_activity = {
        "name": "Test",
        "min_age": 10,
        "max_age": 5,  # min > max
    }

    is_valid, errors = scraper.validate_activity(invalid_activity)
    assert not is_valid
    assert any("age range" in err.lower() for err in errors)


def test_scraper_metrics():
    """Test scraper metrics tracking."""
    db = MagicMock()
    provider = Provider(
        id=1,
        name="Test Provider",
        organization_type="test",
    )

    scraper = MockScraper(db, provider)

    # Initial metrics
    assert scraper.activities_found == 0
    assert scraper.activities_passed == 0
    assert scraper.activities_failed == 0
    assert scraper.duplicates_found == 0

    # Validate a valid activity
    valid_activity = {
        "name": "Test Activity",
        "min_age": 5,
        "max_age": 10,
    }

    scraper.validate_activity(valid_activity)

    # Validate an invalid activity
    invalid_activity = {
        "min_age": 10,
        "max_age": 5,
    }

    is_valid, errors = scraper.validate_activity(invalid_activity)
    assert not is_valid
    assert len(errors) > 0
