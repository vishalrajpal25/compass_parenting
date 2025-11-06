"""
Authorization helpers for multi-tenant access control.
"""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.child import ChildProfile
from app.models.family import Family
from app.models.user import User


async def verify_child_access(
    child_profile_id: int,
    current_user: User,
    db: AsyncSession,
) -> tuple[ChildProfile, Family]:
    """
    Verify current user has access to child profile.

    This helper ensures consistent authorization logic across all endpoints
    and enforces proper multi-tenant data isolation.

    Args:
        child_profile_id: Child profile ID to verify access for
        current_user: Current authenticated user
        db: Database session

    Returns:
        Tuple of (child, family)

    Raises:
        HTTPException: 404 if child not found, 403 if not authorized
    """
    # Fetch child and family in a single query with JOIN
    # This enforces tenant isolation at the query level
    result = await db.execute(
        select(ChildProfile, Family)
        .join(Family, ChildProfile.family_id == Family.id)
        .where(
            ChildProfile.id == child_profile_id,
            ChildProfile.deleted_at.is_(None),  # Exclude soft-deleted
            Family.owner_id == current_user.id,  # Tenant isolation
        )
    )
    row = result.one_or_none()

    if not row:
        # Check if child exists at all (for proper 403 vs 404)
        exists = await db.execute(
            select(ChildProfile).where(
                ChildProfile.id == child_profile_id,
                ChildProfile.deleted_at.is_(None),
            )
        )
        if exists.scalar_one_or_none():
            # Child exists but user doesn't own it - 403 Forbidden
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this child profile",
            )
        else:
            # Child doesn't exist - 404 Not Found
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child profile not found",
            )

    child, family = row
    return child, family
