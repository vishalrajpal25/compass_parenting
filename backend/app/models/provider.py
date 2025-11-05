"""
Provider/organization model for activity providers.
"""
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.activity import Activity


class Provider(Base, TimestampMixin):
    """
    Provider/organization that offers activities.

    Examples: City Recreation Department, YMCA, Little League, etc.
    """

    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Organization details
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    organization_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="e.g., city_rec, ymca, private, nonprofit",
    )

    # Contact information
    website: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Data source information
    data_source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="URL where activity data is scraped from",
    )
    data_source_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="ics, rss, html, json, csv",
    )

    # Quality metrics
    is_verified: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="Manually verified provider",
    )

    # Relationships
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="provider",
    )

    def __repr__(self) -> str:
        return f"<Provider(id={self.id}, name={self.name}, type={self.organization_type})>"
