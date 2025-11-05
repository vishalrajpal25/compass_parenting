"""
Pydantic schemas for authentication.
"""
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)",
    )


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="JWT refresh token")


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    is_active: bool = Field(..., description="User active status")
    created_at: str = Field(..., description="User creation timestamp")

    model_config = {"from_attributes": True}
