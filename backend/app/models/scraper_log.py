"""
from __future__ import annotations

Scraper log model for tracking scraper runs and quality metrics.
"""
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.provider import Provider


class ScraperLog(Base, TimestampMixin):
    """
    Log of scraper runs with quality metrics.

    Tracks pass rate, errors, and automatically demotes sources below 85% pass rate.
    """

    __tablename__ = "scraper_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Provider being scraped
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Run details
    scraper_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="ics, rss, html, json, csv",
    )
    run_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    run_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="success, failed, partial",
    )

    # Metrics
    activities_found: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total activities found",
    )
    activities_passed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Activities that passed validation",
    )
    activities_failed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Activities that failed validation",
    )
    duplicates_found: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Duplicate activities (via canon_hash)",
    )

    # Quality metrics
    pass_rate: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Percentage of activities that passed validation (0-100)",
    )
    http_status: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="HTTP status code from data source",
    )

    # Errors and warnings
    errors: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of error messages",
    )
    warnings: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of warning messages",
    )

    # Validation failures breakdown
    validation_failures: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="""
        {
            "missing_dates": 5,
            "invalid_prices": 2,
            "geocoding_failed": 3,
            "invalid_age_ranges": 1
        }
        """,
    )

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes about the scraper run",
    )

    # Relationships
    provider: Mapped[Provider] = relationship("Provider")

    def __repr__(self) -> str:
        return f"<ScraperLog(id={self.id}, provider_id={self.provider_id}, status={self.status}, pass_rate={self.pass_rate})>"

    @property
    def should_demote(self) -> bool:
        """
        Check if provider should be demoted based on quality thresholds.

        Demotion criteria:
        - Pass rate < 85% for 2 consecutive runs
        - HTTP errors (4xx, 5xx)
        - Broken links > 5%
        """
        if self.pass_rate is not None and self.pass_rate < 85.0:
            return True
        if self.http_status and self.http_status >= 400:
            return True
        return False
