from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FarmerRegistration(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "farmer_registrations"

    registration_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    mobile_e164: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="NEW_IN_PROGRESS", nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="te", nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120))
    village: Mapped[str | None] = mapped_column(String(120))
    mandal: Mapped[str | None] = mapped_column(String(120))
    district: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(120), default="Telangana")
    kyc_reference: Mapped[str | None] = mapped_column(String(80), unique=True)
    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), unique=True
    )


class FarmerProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "farmer_profiles"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    farmer_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    village: Mapped[str | None] = mapped_column(String(120))
    mandal: Mapped[str | None] = mapped_column(String(120))
    district: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(120))
    latitude: Mapped[str | None] = mapped_column(String(32))
    longitude: Mapped[str | None] = mapped_column(String(32))
    kyc_status: Mapped[str] = mapped_column(String(30), default="KYC_PENDING", nullable=False)
    kyc_reference: Mapped[str | None] = mapped_column(String(80), unique=True)
    payout_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)


class BuyerProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "buyer_profiles"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    buyer_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    business_name: Mapped[str] = mapped_column(String(160), nullable=False)
    contact_person: Mapped[str | None] = mapped_column(String(120))
    buyer_type: Mapped[str] = mapped_column(String(40), nullable=False)
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(120))
    latitude: Mapped[str | None] = mapped_column(String(32))
    longitude: Mapped[str | None] = mapped_column(String(32))
    kyc_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    business_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
