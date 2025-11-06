"""
from __future__ import annotations

Venue model for activity locations.
"""
from typing import TYPE_CHECKING, Optional

from geoalchemy2 import Geography
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.activity import Activity


class Venue(Base, TimestampMixin):
    """
    Venue/location where activities take place.

    Uses PostGIS for geospatial queries and geohash for proximity matching.
    """

    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Location details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Geospatial (PostGIS Point)
    location: Mapped[Optional[str]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
    )

    # Geohash for proximity matching (precision 6 = ~1.2km)
    geohash: Mapped[Optional[str]] = mapped_column(
        String(12),
        nullable=True,
        index=True,
        comment="Geohash for proximity matching",
    )

    # Contact information
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Accessibility
    wheelchair_accessible: Mapped[Optional[bool]] = mapped_column(nullable=True)
    parking_available: Mapped[Optional[bool]] = mapped_column(nullable=True)
    public_transit_accessible: Mapped[Optional[bool]] = mapped_column(nullable=True)

    # Relationships
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="venue",
    )

    def __repr__(self) -> str:
        return f"<Venue(id={self.id}, name={self.name}, city={self.city})>"
