"""
Recommendation endpoints with proper multi-tenant isolation.

SECURITY: This module implements defense-in-depth tenant isolation by:
1. Using reusable authorization helper (verify_child_access)
2. Explicit family_id filtering in all queries
3. Single JOIN query for efficient authorization
"""
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps.authorization import verify_child_access
from app.core.deps import CurrentActiveUser, DatabaseSession
from app.models.activity import Activity
from app.models.child import ChildProfile
from app.models.family import Family
from app.models.provider import Provider
from app.models.recommendation import Recommendation
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommender import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=list[RecommendationResponse])
async def generate_recommendations(
    request: RecommendationRequest,
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> list[dict]:
    """
    Generate activity recommendations for a child.

    Uses scoring algorithm + constraint solver to find optimal activities.

    SECURITY: Verifies user owns the family containing the child before
    generating recommendations. Enforces tenant isolation with explicit
    family_id filtering.
    """
    # Authorization check with single JOIN query
    child, family = await verify_child_access(
        request.child_profile_id,
        current_user,
        db,
    )

    # Generate recommendations
    service = RecommendationService(db)
    recommendations = await service.generate_recommendations(
        child_profile_id=request.child_profile_id,
        max_activities=request.max_activities,
    )

    # Load related data with explicit family filtering (defense-in-depth)
    result = await db.execute(
        select(Recommendation)
        .join(Recommendation.child_profile)
        .where(
            Recommendation.child_profile_id == request.child_profile_id,
            ChildProfile.family_id == family.id,  # Explicit tenant isolation
        )
        .order_by(Recommendation.total_score.desc())
        .options(
            selectinload(Recommendation.activity).selectinload(Activity.provider)
        )
    )
    recommendations_with_data = result.scalars().all()

    # Format response
    response = []
    for rec in recommendations_with_data:
        response.append({
            "id": rec.id,
            "child_profile_id": rec.child_profile_id,
            "activity_id": rec.activity_id,
            "activity_name": rec.activity.name,
            "provider_name": rec.activity.provider.name,
            "total_score": float(rec.total_score),
            "fit_score": float(rec.fit_score),
            "practical_score": float(rec.practical_score),
            "goals_score": float(rec.goals_score),
            "score_details": rec.score_details,
            "tier": rec.tier,
            "explanation": rec.explanation,
            "why_good_fit": rec.why_good_fit,
            "considerations": rec.considerations,
            "future_benefits": rec.future_benefits,
            "generated_at": rec.generated_at.isoformat(),
        })

    return response


@router.get("/{child_profile_id}", response_model=list[RecommendationResponse])
async def get_recommendations(
    child_profile_id: int,
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> list[dict]:
    """
    Get existing recommendations for a child.

    SECURITY: Verifies user owns the family containing the child before
    returning recommendations. Enforces tenant isolation with explicit
    family_id filtering.
    """
    # Authorization check with single JOIN query
    child, family = await verify_child_access(child_profile_id, current_user, db)

    # Get recommendations with explicit family filtering (defense-in-depth)
    result = await db.execute(
        select(Recommendation)
        .join(Recommendation.child_profile)
        .where(
            Recommendation.child_profile_id == child_profile_id,
            ChildProfile.family_id == family.id,  # Explicit tenant isolation
        )
        .order_by(Recommendation.total_score.desc())
        .options(
            selectinload(Recommendation.activity).selectinload(Activity.provider)
        )
    )
    recommendations = result.scalars().all()

    # Format response
    response = []
    for rec in recommendations:
        response.append({
            "id": rec.id,
            "child_profile_id": rec.child_profile_id,
            "activity_id": rec.activity_id,
            "activity_name": rec.activity.name,
            "provider_name": rec.activity.provider.name,
            "total_score": float(rec.total_score),
            "fit_score": float(rec.fit_score),
            "practical_score": float(rec.practical_score),
            "goals_score": float(rec.goals_score),
            "score_details": rec.score_details,
            "tier": rec.tier,
            "explanation": rec.explanation,
            "why_good_fit": rec.why_good_fit,
            "considerations": rec.considerations,
            "future_benefits": rec.future_benefits,
            "generated_at": rec.generated_at.isoformat(),
        })

    return response
