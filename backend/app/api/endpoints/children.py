"""
Child profile endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentActiveUser, DatabaseSession
from app.models.child import ChildProfile, PREDEFINED_GOALS
from app.models.family import Family
from app.schemas.child import ChildProfileCreate, ChildProfileResponse, ChildProfileUpdate

router = APIRouter(prefix="/children", tags=["children"])


@router.get("/goals", response_model=list[str])
async def get_predefined_goals() -> list[str]:
    """
    Get predefined goals taxonomy.

    Returns the list of predefined goals that parents can select from.
    """
    return PREDEFINED_GOALS


@router.post("", response_model=ChildProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_child_profile(
    child_in: ChildProfileCreate,
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> ChildProfile:
    """
    Create a child profile for the current user's family.

    The user must have a family profile before creating child profiles.
    """
    # Get user's family
    result = await db.execute(
        select(Family).where(Family.owner_id == current_user.id)
    )
    family = result.scalar_one_or_none()

    if not family:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must create a family profile before adding children",
        )

    # Convert temperament and constraints to dict for JSONB storage
    temperament_dict = None
    if child_in.temperament:
        temperament_dict = child_in.temperament.model_dump()

    constraints_dict = None
    if child_in.constraints:
        # Convert ScheduleWindow objects to dicts
        constraints_data = child_in.constraints.model_dump()
        if constraints_data.get("schedule_windows"):
            constraints_data["schedule_windows"] = [
                window for window in constraints_data["schedule_windows"]
            ]
        constraints_dict = constraints_data

    # Create child profile
    child = ChildProfile(
        family_id=family.id,
        name=child_in.name,
        birth_date=child_in.birth_date,
        temperament=temperament_dict,
        primary_goal=child_in.primary_goal,
        secondary_goal=child_in.secondary_goal,
        tertiary_goal=child_in.tertiary_goal,
        custom_goals=child_in.custom_goals,
        constraints=constraints_dict,
        preferred_activity_types=child_in.preferred_activity_types,
        notes=child_in.notes,
    )

    db.add(child)
    await db.commit()
    await db.refresh(child)

    return child


@router.get("", response_model=list[ChildProfileResponse])
async def list_children(
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> list[ChildProfile]:
    """
    List all children in the current user's family.
    """
    # Get user's family
    result = await db.execute(
        select(Family).where(Family.owner_id == current_user.id)
    )
    family = result.scalar_one_or_none()

    if not family:
        return []

    # Get children
    result = await db.execute(
        select(ChildProfile)
        .where(ChildProfile.family_id == family.id)
        .where(ChildProfile.deleted_at.is_(None))
    )
    children = result.scalars().all()

    return list(children)


@router.get("/{child_id}", response_model=ChildProfileResponse)
async def get_child_profile(
    child_id: int,
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> ChildProfile:
    """
    Get a specific child profile.

    Only returns children belonging to the current user's family.
    """
    # Get user's family
    result = await db.execute(
        select(Family).where(Family.owner_id == current_user.id)
    )
    family = result.scalar_one_or_none()

    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found",
        )

    # Get child
    result = await db.execute(
        select(ChildProfile)
        .where(ChildProfile.id == child_id)
        .where(ChildProfile.family_id == family.id)
        .where(ChildProfile.deleted_at.is_(None))
    )
    child = result.scalar_one_or_none()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found",
        )

    return child


@router.patch("/{child_id}", response_model=ChildProfileResponse)
async def update_child_profile(
    child_id: int,
    child_update: ChildProfileUpdate,
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> ChildProfile:
    """
    Update a child profile.

    Only updates children belonging to the current user's family.
    """
    # Get user's family
    result = await db.execute(
        select(Family).where(Family.owner_id == current_user.id)
    )
    family = result.scalar_one_or_none()

    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found",
        )

    # Get child
    result = await db.execute(
        select(ChildProfile)
        .where(ChildProfile.id == child_id)
        .where(ChildProfile.family_id == family.id)
        .where(ChildProfile.deleted_at.is_(None))
    )
    child = result.scalar_one_or_none()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found",
        )

    # Update fields
    update_data = child_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(child, field, value)

    await db.commit()
    await db.refresh(child)

    return child


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child_profile(
    child_id: int,
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> None:
    """
    Soft delete a child profile.

    Uses soft delete to preserve data for potential recovery.
    """
    # Get user's family
    result = await db.execute(
        select(Family).where(Family.owner_id == current_user.id)
    )
    family = result.scalar_one_or_none()

    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found",
        )

    # Get child
    result = await db.execute(
        select(ChildProfile)
        .where(ChildProfile.id == child_id)
        .where(ChildProfile.family_id == family.id)
        .where(ChildProfile.deleted_at.is_(None))
    )
    child = result.scalar_one_or_none()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found",
        )

    # Soft delete
    child.soft_delete()
    await db.commit()
