"""
Pydantic schemas for child profiles.
"""
from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class TemperamentSchema(BaseModel):
    """Schema for child temperament."""

    big_five: dict[str, int] = Field(
        ...,
        description="Big Five personality traits (1-5 scale)",
        example={
            "openness": 3,
            "conscientiousness": 4,
            "extraversion": 2,
            "agreeableness": 5,
            "neuroticism": 2,
        },
    )
    sensory_sensitivity: str = Field(
        ...,
        description="Sensory sensitivity level",
        pattern="^(low|medium|high)$",
    )
    intensity_preference: str = Field(
        ...,
        description="Intensity preference level",
        pattern="^(low|moderate|high)$",
    )
    social_preference: str = Field(
        ...,
        description="Social activity preference",
        pattern="^(solo|small_group|team)$",
    )


class ScheduleWindow(BaseModel):
    """Schema for schedule availability window."""

    day: str = Field(
        ...,
        description="Day of week",
        pattern="^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$",
    )
    start: str = Field(..., description="Start time (HH:MM format)", pattern=r"^\d{2}:\d{2}$")
    end: str = Field(..., description="End time (HH:MM format)", pattern=r"^\d{2}:\d{2}$")


class ConstraintsSchema(BaseModel):
    """Schema for child constraints."""

    schedule_windows: list[ScheduleWindow] | None = Field(
        None,
        description="Available schedule windows",
    )
    max_activities_per_week: int | None = Field(
        None,
        ge=1,
        le=7,
        description="Maximum activities per week",
    )
    special_needs: str | None = Field(
        None,
        description="Special needs or accommodations",
    )
    dietary_restrictions: str | None = Field(
        None,
        description="Dietary restrictions",
    )
    medical_notes: str | None = Field(
        None,
        description="Medical considerations",
    )
    neurodiversity_notes: str | None = Field(
        None,
        description="Neurodiversity considerations",
    )


class ChildProfileCreate(BaseModel):
    """Schema for creating a child profile."""

    name: str = Field(..., min_length=1, max_length=100, description="Child's name")
    birth_date: date = Field(..., description="Birth date (YYYY-MM-DD)")
    temperament: TemperamentSchema | None = Field(None, description="Temperament profile")
    primary_goal: str | None = Field(None, max_length=100, description="Primary goal")
    secondary_goal: str | None = Field(None, max_length=100, description="Secondary goal")
    tertiary_goal: str | None = Field(None, max_length=100, description="Tertiary goal")
    custom_goals: list[str] | None = Field(
        None,
        description="Custom free-form goals",
    )
    constraints: ConstraintsSchema | None = Field(None, description="Scheduling constraints")
    preferred_activity_types: list[str] | None = Field(
        None,
        description="Preferred activity types (e.g., sports, arts, stem)",
    )
    notes: str | None = Field(
        None,
        description="Additional notes about child",
    )


class ChildProfileUpdate(BaseModel):
    """Schema for updating a child profile."""

    name: str | None = None
    birth_date: date | None = None
    temperament: dict[str, Any] | None = None
    primary_goal: str | None = None
    secondary_goal: str | None = None
    tertiary_goal: str | None = None
    custom_goals: list[str] | None = None
    constraints: dict[str, Any] | None = None
    preferred_activity_types: list[str] | None = None
    notes: str | None = None


class ChildProfileResponse(BaseModel):
    """Schema for child profile response."""

    id: int = Field(..., description="Child profile ID")
    family_id: int = Field(..., description="Family ID")
    name: str = Field(..., description="Child's name")
    birth_date: date = Field(..., description="Birth date")
    age: int = Field(..., description="Current age (calculated)")
    temperament: dict[str, Any] | None = Field(None, description="Temperament profile")
    primary_goal: str | None = Field(None, description="Primary goal")
    secondary_goal: str | None = Field(None, description="Secondary goal")
    tertiary_goal: str | None = Field(None, description="Tertiary goal")
    custom_goals: list[str] | None = Field(None, description="Custom goals")
    constraints: dict[str, Any] | None = Field(None, description="Constraints")
    preferred_activity_types: list[str] | None = Field(None, description="Activity types")
    notes: str | None = Field(None, description="Notes")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}
