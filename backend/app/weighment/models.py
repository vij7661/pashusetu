from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MandalCentre(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "mandal_centres"

    centre_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    village: Mapped[str | None] = mapped_column(String(120))
    mandal: Mapped[str | None] = mapped_column(String(120))
    district: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(120), default="Telangana")
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class OperatorProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "operator_profiles"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    operator_code: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    centre_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("mandal_centres.id", ondelete="RESTRICT"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ScaleDevice(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "scale_devices"

    scale_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    centre_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("mandal_centres.id", ondelete="RESTRICT"), nullable=False
    )
    vendor: Mapped[str | None] = mapped_column(String(120))
    model: Mapped[str | None] = mapped_column(String(120))
    bluetooth_identifier: Mapped[str | None] = mapped_column(String(160))
    calibration_status: Mapped[str] = mapped_column(String(30), default="VALID", nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class WeighmentSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "weighment_sessions"
    __table_args__ = (
        CheckConstraint("target_type IN ('GOAT','LOT')", name="ck_weighment_target_type"),
    )

    weighment_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    target_type: Mapped[str] = mapped_column(String(10), nullable=False)
    target_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    farmer_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("farmer_profiles.id", ondelete="RESTRICT"), nullable=False
    )
    operator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("operator_profiles.id", ondelete="RESTRICT"), nullable=False
    )
    centre_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("mandal_centres.id", ondelete="RESTRICT"), nullable=False
    )
    scale_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("scale_devices.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default="LIVE", nullable=False)
    reweigh_of_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("weighment_sessions.id", ondelete="RESTRICT")
    )


class WeightReading(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "weight_readings"

    weighment_session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("weighment_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    gross_kg: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    tare_kg: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    net_kg: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    stable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class FarmerWeighmentAcknowledgement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "farmer_weighment_acknowledgements"
    __table_args__ = (
        UniqueConstraint("weighment_session_id", name="uq_weighment_ack"),
    )

    weighment_session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("weighment_sessions.id", ondelete="CASCADE"), nullable=False
    )
    farmer_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("farmer_profiles.id", ondelete="RESTRICT"), nullable=False
    )
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    method: Mapped[str] = mapped_column(String(30), default="APP_CONFIRMATION", nullable=False)


class WeighmentReceipt(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "weighment_receipts"

    weighment_session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("weighment_sessions.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    receipt_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    qr_payload: Mapped[str] = mapped_column(Text, nullable=False)
    print_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
