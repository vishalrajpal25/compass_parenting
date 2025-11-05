"""
Family profile endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentActiveUser, DatabaseSession
from app.models.family import Family
from app.schemas.family import FamilyCreate, FamilyResponse, FamilyUpdate

router = APIRouter(prefix="/families", tags=["families"])


@router.post("", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    family_in: FamilyCreate,
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> Family:
    """
    Create a family profile for the current user.

    Each user can only have one family profile.
    """
    # Check if user already has a family
    result = await db.execute(
        select(Family).where(Family.owner_id == current_user.id)
    )
    existing_family = result.scalar_one_or_none()

    if existing_family:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a family profile",
        )

    # Create family
    family = Family(
        owner_id=current_user.id,
        **family_in.model_dump(),
    )

    db.add(family)
    await db.commit()
    await db.refresh(family)

    return family


@router.get("/me", response_model=FamilyResponse)
async def get_my_family(
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> Family:
    """
    Get the current user's family profile.
    """
    result = await db.execute(
        select(Family).where(Family.owner_id == current_user.id)
    )
    family = result.scalar_one_or_none()

    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found",
        )

    return family


@router.patch("/me", response_model=FamilyResponse)
async def update_my_family(
    family_update: FamilyUpdate,
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> Family:
    """
    Update the current user's family profile.
    """
    result = await db.execute(
        select(Family).where(Family.owner_id == current_user.id)
    )
    family = result.scalar_one_or_none()

    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found",
        )

    # Update fields
    update_data = family_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(family, field, value)

    await db.commit()
    await db.refresh(family)

    return family


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_family(
    current_user: CurrentActiveUser,
    db: DatabaseSession,
) -> None:
    """
    Delete the current user's family profile.

    This will also delete all associated child profiles (cascade).
    """
    result = await db.execute(
        select(Family).where(Family.owner_id == current_user.id)
    )
    family = result.scalar_one_or_none()

    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Family profile not found",
        )

    await db.delete(family)
    await db.commit()
