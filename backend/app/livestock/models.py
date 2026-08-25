from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Goat(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "goats"

    goat_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    farmer_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("farmer_profiles.id", ondelete="CASCADE"), nullable=False
    )
    breed: Mapped[str | None] = mapped_column(String(80))
    sex: Mapped[str | None] = mapped_column(String(10))
    age_months: Mapped[int | None] = mapped_column(Integer)
    health_notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)


class Lot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "lots"
    __table_args__ = (CheckConstraint("declared_quantity > 0", name="ck_lot_quantity_positive"),)

    lot_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    farmer_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("farmer_profiles.id", ondelete="CASCADE"), nullable=False
    )
    declared_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    breed_summary: Mapped[str | None] = mapped_column(String(160))
    sex_summary: Mapped[str | None] = mapped_column(String(160))
    age_summary: Mapped[str | None] = mapped_column(String(160))
    health_notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)


class LotGoat(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "lot_goats"

    lot_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("lots.id", ondelete="CASCADE"), nullable=False
    )
    goat_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("goats.id", ondelete="CASCADE"), nullable=False, unique=True
    )


class EvidenceAsset(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "evidence_assets"

    owner_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    owner_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(40), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    sha256_hex: Mapped[str | None] = mapped_column(String(64))
    captured_by_user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    status: Mapped[str] = mapped_column(String(20), default="UPLOADED", nullable=False)
