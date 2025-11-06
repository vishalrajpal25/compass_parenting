"""
from __future__ import annotations

Child profile model with temperament, goals, and constraints.
"""
from datetime import date
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.family import Family


# Predefined goals taxonomy based on parent-advocate persona
PREDEFINED_GOALS = [
    "Build Confidence",
    "College Prep Skills",
    "Physical Fitness",
    "Creative Expression",
    "Social Skills",
    "STEM Learning",
    "Language Development",
    "Cultural Connection",
    "Emotional Regulation",
    "Leadership",
]


class ChildProfile(Base, TimestampMixin, SoftDeleteMixin):
    """
    Child profile with temperament, goals, and scheduling constraints.

    Temperament uses JSONB with:
    - Big Five personality traits (openness, conscientiousness, extraversion, agreeableness, neuroticism)
    - Sensory sensitivity (low, medium, high)
    - Intensity preference (low, moderate, high)
    - Social preference (solo, small_group, team)

    Goals include predefined taxonomy + custom free-form goals.
    """

    __tablename__ = "child_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Temperament (JSONB)
    temperament: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="""
        Big Five traits (1-5 scale each):
        {
            "big_five": {
                "openness": 3,
                "conscientiousness": 4,
                "extraversion": 2,
                "agreeableness": 5,
                "neuroticism": 2
            },
            "sensory_sensitivity": "medium",
            "intensity_preference": "moderate",
            "social_preference": "small_group"
        }
        """,
    )

    # Goals (predefined + custom)
    primary_goal: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    secondary_goal: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tertiary_goal: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    custom_goals: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Free-form goals for future taxonomy enrichment",
    )

    # Constraints (JSONB)
    constraints: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="""
        Scheduling and special considerations:
        {
            "schedule_windows": [
                {"day": "monday", "start": "16:00", "end": "18:00"},
                {"day": "saturday", "start": "09:00", "end": "12:00"}
            ],
            "max_activities_per_week": 3,
            "special_needs": "Autism spectrum, visual learner",
            "dietary_restrictions": "Vegetarian",
            "medical_notes": "Asthma, needs inhaler access",
            "neurodiversity_notes": "Prefers structured activities with clear rules"
        }
        """,
    )

    # Activity preferences
    preferred_activity_types: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="e.g., ['sports', 'arts', 'stem', 'music']",
    )

    # Notes (free-form text for parent context)
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Parent notes about child interests, strengths, concerns",
    )

    # Relationships
    family: Mapped["Family"] = relationship("Family", back_populates="children")

    def __repr__(self) -> str:
        return f"<ChildProfile(id={self.id}, name={self.name}, family_id={self.family_id})>"

    @property
    def age(self) -> int:
        """Calculate current age from birth date."""
        from datetime import datetime
        today = datetime.now().date()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
