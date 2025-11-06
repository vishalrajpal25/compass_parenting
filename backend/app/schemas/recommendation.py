"""
Pydantic schemas for recommendations.
"""
from typing import Any, Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Schema for requesting recommendations."""

    child_profile_id: int = Field(..., description="Child profile ID")
    max_activities: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of activities to recommend",
    )


class RecommendationResponse(BaseModel):
    """Schema for recommendation response."""

    id: int = Field(..., description="Recommendation ID")
    child_profile_id: int = Field(..., description="Child profile ID")
    activity_id: int = Field(..., description="Activity ID")
    activity_name: str = Field(..., description="Activity name")
    provider_name: str = Field(..., description="Provider name")
    total_score: float = Field(..., description="Total score (0-100)")
    fit_score: float = Field(..., description="Fit score component")
    practical_score: float = Field(..., description="Practical score component")
    goals_score: float = Field(..., description="Goals score component")
    score_details: dict[str, Any] = Field(..., description="Detailed score breakdown")
    tier: str = Field(..., description="Recommendation tier (primary, budget_saver, stretch)")
    explanation: Optional[str] = Field(None, description="Human-readable explanation")
    why_good_fit: Optional[list[str]] = Field(None, description="Why it's a good fit")
    considerations: Optional[list[str]] = Field(None, description="Things to consider")
    future_benefits: Optional[list[str]] = Field(None, description="Long-term benefits")
    generated_at: str = Field(..., description="Generation timestamp")

    model_config = {"from_attributes": True}
