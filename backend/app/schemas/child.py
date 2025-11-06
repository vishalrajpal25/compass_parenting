"""
Pydantic schemas for child profiles.
"""
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_serializer


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

    schedule_windows: Optional[list[ScheduleWindow]] = Field(
        None,
        description="Available schedule windows",
    )
    max_activities_per_week: Optional[int] = Field(
        None,
        ge=1,
        le=7,
        description="Maximum activities per week",
    )
    special_needs: Optional[str] = Field(
        None,
        description="Special needs or accommodations",
    )
    dietary_restrictions: Optional[str] = Field(
        None,
        description="Dietary restrictions",
    )
    medical_notes: Optional[str] = Field(
        None,
        description="Medical considerations",
    )
    neurodiversity_notes: Optional[str] = Field(
        None,
        description="Neurodiversity considerations",
    )


class ChildProfileCreate(BaseModel):
    """Schema for creating a child profile."""

    name: str = Field(..., min_length=1, max_length=100, description="Child's name")
    birth_date: date = Field(..., description="Birth date (YYYY-MM-DD)")
    temperament: Optional[TemperamentSchema] = Field(None, description="Temperament profile")
    primary_goal: Optional[str] = Field(None, max_length=100, description="Primary goal")
    secondary_goal: Optional[str] = Field(None, max_length=100, description="Secondary goal")
    tertiary_goal: Optional[str] = Field(None, max_length=100, description="Tertiary goal")
    custom_goals: Optional[list[str]] = Field(
        None,
        description="Custom free-form goals",
    )
    constraints: Optional[ConstraintsSchema] = Field(None, description="Scheduling constraints")
    preferred_activity_types: Optional[list[str]] = Field(
        None,
        description="Preferred activity types (e.g., sports, arts, stem)",
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about child",
    )


class ChildProfileUpdate(BaseModel):
    """Schema for updating a child profile."""

    name: Optional[str] = None
    birth_date: Optional[date] = None
    temperament: Optional[dict[str, Any]] = None
    primary_goal: Optional[str] = None
    secondary_goal: Optional[str] = None
    tertiary_goal: Optional[str] = None
    custom_goals: Optional[list[str]] = None
    constraints: Optional[dict[str, Any]] = None
    preferred_activity_types: Optional[list[str]] = None
    notes: Optional[str] = None


class ChildProfileResponse(BaseModel):
    """Schema for child profile response."""

    id: int = Field(..., description="Child profile ID")
    family_id: int = Field(..., description="Family ID")
    name: str = Field(..., description="Child's name")
    birth_date: date = Field(..., description="Birth date")
    age: int = Field(..., description="Current age (calculated)")
    temperament: Optional[dict[str, Any]] = Field(None, description="Temperament profile")
    primary_goal: Optional[str] = Field(None, description="Primary goal")
    secondary_goal: Optional[str] = Field(None, description="Secondary goal")
    tertiary_goal: Optional[str] = Field(None, description="Tertiary goal")
    custom_goals: Optional[list[str]] = Field(None, description="Custom goals")
    constraints: Optional[dict[str, Any]] = Field(None, description="Constraints")
    preferred_activity_types: Optional[list[str]] = Field(None, description="Activity types")
    notes: Optional[str] = Field(None, description="Notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return dt.isoformat()

    model_config = {"from_attributes": True}
