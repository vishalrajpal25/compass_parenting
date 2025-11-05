"""
Activity catalog endpoints.
"""
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import DatabaseSession
from app.models.activity import Activity
from app.models.provider import Provider
from app.models.venue import Venue
from app.schemas.activity import ActivityResponse, ProviderResponse, VenueResponse

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=list[ActivityResponse])
async def list_activities(
    db: DatabaseSession,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    activity_type: str | None = Query(None, description="Filter by activity type"),
    min_age: int | None = Query(None, ge=0, le=18, description="Filter by minimum age"),
    max_age: int | None = Query(None, ge=0, le=18, description="Filter by maximum age"),
    is_active: bool = Query(True, description="Filter by active status"),
) -> list[Activity]:
    """
    List activities with optional filters.

    Returns paginated list of activities.
    """
    query = select(Activity).where(Activity.is_active == is_active)

    # Apply filters
    if activity_type:
        query = query.where(Activity.activity_type == activity_type)

    if min_age is not None:
        query = query.where(
            (Activity.min_age <= min_age) | (Activity.min_age.is_(None))
        )

    if max_age is not None:
        query = query.where(
            (Activity.max_age >= max_age) | (Activity.max_age.is_(None))
        )

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    activities = result.scalars().all()

    return list(activities)


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    db: DatabaseSession,
) -> Activity:
    """
    Get a specific activity by ID.
    """
    result = await db.execute(
        select(Activity).where(Activity.id == activity_id)
    )
    activity = result.scalar_one_or_none()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )

    return activity


@router.get("/providers", response_model=list[ProviderResponse])
async def list_providers(
    db: DatabaseSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> list[Provider]:
    """
    List activity providers.
    """
    result = await db.execute(
        select(Provider).offset(skip).limit(limit)
    )
    providers = result.scalars().all()

    return list(providers)


@router.get("/venues", response_model=list[VenueResponse])
async def list_venues(
    db: DatabaseSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> list[Venue]:
    """
    List activity venues.
    """
    result = await db.execute(
        select(Venue).offset(skip).limit(limit)
    )
    venues = result.scalars().all()

    return list(venues)
