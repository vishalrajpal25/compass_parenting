"""
from __future__ import annotations

Activity model for enrichment activities.
"""
from datetime import date, time
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text, Time
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.provider import Provider
    from app.models.venue import Venue


class Activity(Base, TimestampMixin):
    """
    Enrichment activity with schedule, pricing, and attributes.

    De-duplication via canon_hash (normalized name + fuzzy date + geohash6 + org).
    """

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign keys
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    venue_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("venues.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="sports, arts, stem, music, language, etc.",
    )

    # Schedule (RRULE support for recurring events)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    rrule: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="iCalendar RRULE for recurring events",
    )

    # Days of week (for simple recurring patterns)
    days_of_week: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment='e.g., ["monday", "wednesday", "friday"]',
    )

    # Age restrictions
    min_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    age_range_text: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment='Original text like "5-7 years" or "Kindergarten-2nd grade"',
    )

    # Pricing (in cents)
    price_cents: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Price in cents (e.g., 5000 = $50.00)",
    )
    price_text: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment='Original price text like "$50/month" or "Free"',
    )
    has_scholarship: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="Financial assistance available",
    )

    # Registration
    registration_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    registration_deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    registration_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="open, closed, waitlist, full",
    )
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Activity attributes (JSONB for flexibility)
    attributes: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="""
        {
            "intensity_level": "low|moderate|high",
            "team_vs_solo": "team|small_group|solo",
            "indoor_outdoor": "indoor|outdoor|both",
            "neurodiversity_friendly": true,
            "sensory_load": "low|medium|high",
            "prerequisites": ["swimming basics"],
            "equipment_needed": ["tennis racket"],
            "drop_in_allowed": true
        }
        """,
    )

    # De-duplication
    canon_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        unique=True,
        comment="SHA256 hash for de-duplication (normalized name + fuzzy date ±3 + geohash6 + org)",
    )

    # Data quality
    source_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Original URL where this activity was found",
    )
    last_verified: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Last date this activity was verified/scraped",
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="Whether activity is currently active/available",
    )

    # Relationships
    provider: Mapped["Provider"] = relationship("Provider", back_populates="activities")
    venue: Mapped["Venue | None"] = relationship("Venue", back_populates="activities")

    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, name={self.name}, provider_id={self.provider_id})>"
