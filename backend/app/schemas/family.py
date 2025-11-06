"""
Pydantic schemas for family profiles.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_serializer


class FamilyCreate(BaseModel):
    """Schema for creating a family profile."""

    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State")
    zip_code: Optional[str] = Field(None, max_length=10, description="ZIP code")
    timezone: str = Field(
        default="America/Los_Angeles",
        description="Timezone (e.g., America/Los_Angeles)",
    )
    budget_monthly: Optional[int] = Field(
        None,
        ge=0,
        description="Monthly budget in cents (e.g., 50000 = $500.00)",
    )
    calendar_ics_url: Optional[str] = Field(
        None,
        description="ICS calendar URL for importing family schedule",
    )
    partner_email: Optional[EmailStr] = Field(
        None,
        description="Partner email for shared access",
    )


class FamilyUpdate(BaseModel):
    """Schema for updating a family profile."""

    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    timezone: Optional[str] = None
    budget_monthly: Optional[int] = None
    calendar_ics_url: Optional[str] = None
    partner_email: Optional[EmailStr] = None


class FamilyResponse(BaseModel):
    """Schema for family response."""

    id: int = Field(..., description="Family ID")
    owner_id: int = Field(..., description="Owner user ID")
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    timezone: str = Field(..., description="Timezone")
    budget_monthly: Optional[int] = Field(None, description="Monthly budget in cents")
    calendar_ics_url: Optional[str] = Field(None, description="Calendar ICS URL")
    partner_email: Optional[str] = Field(None, description="Partner email")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime to ISO format string."""
        return dt.isoformat()

    model_config = {"from_attributes": True}
