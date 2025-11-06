"""
from __future__ import annotations

Recommendation model for storing child-specific activity recommendations.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.child import ChildProfile


class Recommendation(Base, TimestampMixin):
    """
    Activity recommendation for a specific child.

    Stores scoring breakdown, explanation, and recommendation tier.
    """

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign keys
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Denormalized for efficient tenant isolation queries",
    )
    child_profile_id: Mapped[int] = mapped_column(
        ForeignKey("child_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Scoring (0-100 scale)
    total_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        index=True,
        comment="Total recommendation score (0-100)",
    )

    # Score breakdown
    fit_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Fit score component (50% weight)",
    )
    practical_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Practical score component (30% weight)",
    )
    goals_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Goals alignment score (20% weight)",
    )

    # Detailed scoring breakdown (JSONB)
    score_details: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="""
        Detailed breakdown of all scoring components:
        {
            "fit": {
                "age_band_match": 15.0,
                "intensity_match": 10.0,
                "sensory_tolerance": 8.0,
                "team_vs_solo": 5.0,
                "prerequisites": 5.0,
                "neurodiversity": 5.0
            },
            "practical": {
                "commute_time": 10.0,
                "schedule_fit": 9.0,
                "price_vs_budget": 5.0,
                "scholarship_bonus": 2.5,
                "transit_accessible": 2.5
            },
            "goals": {
                "primary_goal": 10.0,
                "secondary_goal": 6.0,
                "tertiary_goal": 4.0
            }
        }
        """,
    )

    # Recommendation tier
    tier: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True,
        comment="primary, budget_saver, stretch",
    )

    # Explanation
    explanation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable explanation of why this activity is recommended",
    )

    # Why it's a good fit (parent-advocate style)
    why_good_fit: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment='["Matches their love of hands-on projects", "Builds confidence through small wins"]',
    )

    # What to watch for (transparency)
    considerations: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment='["Requires 30-min commute on Saturdays", "Class size is 20+ kids"]',
    )

    # Future benefits (connect to long-term outcomes)
    future_benefits: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment='["STEM skills for middle school readiness", "Problem-solving practice"]',
    )

    # Metadata
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(),
        comment="When this recommendation was generated",
    )

    # Relationships
    child_profile: Mapped["ChildProfile"] = relationship("ChildProfile")
    activity: Mapped["Activity"] = relationship("Activity")

    def __repr__(self) -> str:
        return f"<Recommendation(id={self.id}, child_profile_id={self.child_profile_id}, activity_id={self.activity_id}, score={self.total_score}, tier={self.tier})>"
