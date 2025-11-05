"""
Pydantic schemas for activities.
"""
from datetime import date, time
from typing import Any

from pydantic import BaseModel, Field


class ActivityResponse(BaseModel):
    """Schema for activity response."""

    id: int = Field(..., description="Activity ID")
    provider_id: int = Field(..., description="Provider ID")
    venue_id: int | None = Field(None, description="Venue ID")
    name: str = Field(..., description="Activity name")
    description: str | None = Field(None, description="Activity description")
    activity_type: str | None = Field(None, description="Activity type")
    start_date: date | None = Field(None, description="Start date")
    end_date: date | None = Field(None, description="End date")
    start_time: time | None = Field(None, description="Start time")
    end_time: time | None = Field(None, description="End time")
    rrule: str | None = Field(None, description="RRULE for recurring events")
    days_of_week: list[str] | None = Field(None, description="Days of week")
    min_age: int | None = Field(None, description="Minimum age")
    max_age: int | None = Field(None, description="Maximum age")
    age_range_text: str | None = Field(None, description="Original age range text")
    price_cents: int | None = Field(None, description="Price in cents")
    price_text: str | None = Field(None, description="Original price text")
    has_scholarship: bool = Field(..., description="Scholarship available")
    registration_url: str | None = Field(None, description="Registration URL")
    registration_deadline: date | None = Field(None, description="Registration deadline")
    registration_status: str | None = Field(None, description="Registration status")
    attributes: dict[str, Any] | None = Field(None, description="Activity attributes")
    is_active: bool = Field(..., description="Is active")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class ProviderResponse(BaseModel):
    """Schema for provider response."""

    id: int = Field(..., description="Provider ID")
    name: str = Field(..., description="Provider name")
    description: str | None = Field(None, description="Description")
    organization_type: str | None = Field(None, description="Organization type")
    website: str | None = Field(None, description="Website")
    created_at: str = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class VenueResponse(BaseModel):
    """Schema for venue response."""

    id: int = Field(..., description="Venue ID")
    name: str = Field(..., description="Venue name")
    address: str | None = Field(None, description="Street address")
    city: str | None = Field(None, description="City")
    state: str | None = Field(None, description="State")
    zip_code: str | None = Field(None, description="ZIP code")
    wheelchair_accessible: bool | None = Field(None, description="Wheelchair accessible")
    parking_available: bool | None = Field(None, description="Parking available")
    created_at: str = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}
