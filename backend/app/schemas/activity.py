"""
Pydantic schemas for activities.
"""
from datetime import date, datetime, time
from typing import Any, Optional

from pydantic import BaseModel, Field, field_serializer


class ActivityResponse(BaseModel):
    """Schema for activity response."""

    id: int = Field(..., description="Activity ID")
    provider_id: int = Field(..., description="Provider ID")
    venue_id: Optional[int] = Field(None, description="Venue ID")
    name: str = Field(..., description="Activity name")
    description: Optional[str] = Field(None, description="Activity description")
    activity_type: Optional[str] = Field(None, description="Activity type")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    start_time: Optional[time] = Field(None, description="Start time")
    end_time: Optional[time] = Field(None, description="End time")
    rrule: Optional[str] = Field(None, description="RRULE for recurring events")
    days_of_week: Optional[list[str]] = Field(None, description="Days of week")
    min_age: Optional[int] = Field(None, description="Minimum age")
    max_age: Optional[int] = Field(None, description="Maximum age")
    age_range_text: Optional[str] = Field(None, description="Original age range text")
    price_cents: Optional[int] = Field(None, description="Price in cents")
    price_text: Optional[str] = Field(None, description="Original price text")
    has_scholarship: bool = Field(..., description="Scholarship available")
    registration_url: Optional[str] = Field(None, description="Registration URL")
    registration_deadline: Optional[date] = Field(None, description="Registration deadline")
    registration_status: Optional[str] = Field(None, description="Registration status")
    attributes: Optional[dict[str, Any]] = Field(None, description="Activity attributes")
    is_active: bool = Field(..., description="Is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return dt.isoformat()

    model_config = {"from_attributes": True}


class ProviderResponse(BaseModel):
    """Schema for provider response."""

    id: int = Field(..., description="Provider ID")
    name: str = Field(..., description="Provider name")
    description: Optional[str] = Field(None, description="Description")
    organization_type: Optional[str] = Field(None, description="Organization type")
    website: Optional[str] = Field(None, description="Website")
    created_at: datetime = Field(..., description="Creation timestamp")

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return dt.isoformat()

    model_config = {"from_attributes": True}


class VenueResponse(BaseModel):
    """Schema for venue response."""

    id: int = Field(..., description="Venue ID")
    name: str = Field(..., description="Venue name")
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    wheelchair_accessible: Optional[bool] = Field(None, description="Wheelchair accessible")
    parking_available: Optional[bool] = Field(None, description="Parking available")
    created_at: datetime = Field(..., description="Creation timestamp")

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return dt.isoformat()

    model_config = {"from_attributes": True}
