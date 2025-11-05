"""
User model for authentication.
"""
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.family import Family


class User(Base, TimestampMixin):
    """
    User model for authentication.

    Represents a parent/guardian who can manage family and child profiles.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    family: Mapped["Family | None"] = relationship(
        "Family",
        back_populates="owner",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
