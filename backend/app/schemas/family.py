"""
Pydantic schemas for family profiles.
"""
from pydantic import BaseModel, EmailStr, Field


class FamilyCreate(BaseModel):
    """Schema for creating a family profile."""

    address: str | None = Field(None, description="Street address")
    city: str | None = Field(None, description="City")
    state: str | None = Field(None, max_length=50, description="State")
    zip_code: str | None = Field(None, max_length=10, description="ZIP code")
    timezone: str = Field(
        default="America/Los_Angeles",
        description="Timezone (e.g., America/Los_Angeles)",
    )
    budget_monthly: int | None = Field(
        None,
        ge=0,
        description="Monthly budget in cents (e.g., 50000 = $500.00)",
    )
    calendar_ics_url: str | None = Field(
        None,
        description="ICS calendar URL for importing family schedule",
    )
    partner_email: EmailStr | None = Field(
        None,
        description="Partner email for shared access",
    )


class FamilyUpdate(BaseModel):
    """Schema for updating a family profile."""

    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    timezone: str | None = None
    budget_monthly: int | None = None
    calendar_ics_url: str | None = None
    partner_email: EmailStr | None = None


class FamilyResponse(BaseModel):
    """Schema for family response."""

    id: int = Field(..., description="Family ID")
    owner_id: int = Field(..., description="Owner user ID")
    address: str | None = Field(None, description="Street address")
    city: str | None = Field(None, description="City")
    state: str | None = Field(None, description="State")
    zip_code: str | None = Field(None, description="ZIP code")
    timezone: str = Field(..., description="Timezone")
    budget_monthly: int | None = Field(None, description="Monthly budget in cents")
    calendar_ics_url: str | None = Field(None, description="Calendar ICS URL")
    partner_email: str | None = Field(None, description="Partner email")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}
