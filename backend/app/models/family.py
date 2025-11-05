"""
Family model for household profile.
"""
from typing import TYPE_CHECKING

from geoalchemy2 import Geography
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.child import ChildProfile
    from app.models.user import User


class Family(Base, TimestampMixin):
    """
    Family/household profile.

    Represents a household with geographic location, budget, and calendar preferences.
    Owned by a User (parent/guardian).
    """

    __tablename__ = "families"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Location (PostGIS Point)
    location: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
    )
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Timezone (e.g., "America/Los_Angeles")
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="America/Los_Angeles",
        nullable=False,
    )

    # Budget constraints
    budget_monthly: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Monthly budget in cents (e.g., 50000 = $500.00)",
    )

    # Calendar import URL (ICS)
    calendar_ics_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Partner email for sharing (token-based collaboration)
    partner_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="family")
    children: Mapped[list["ChildProfile"]] = relationship(
        "ChildProfile",
        back_populates="family",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Family(id={self.id}, owner_id={self.owner_id}, city={self.city})>"
