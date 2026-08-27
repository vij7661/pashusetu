from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class TransportAssignment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "transport_assignments"
    transaction_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    transporter_name: Mapped[str] = mapped_column(String(120), nullable=False)
    driver_name: Mapped[str] = mapped_column(String(120), nullable=False)
    driver_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    vehicle_number: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ASSIGNED", nullable=False)


class PickupRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "pickup_records"
    transaction_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    qr_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    goat_count: Mapped[int] = mapped_column(Integer, nullable=False)
    loading_video_evidence_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    departure_note: Mapped[str | None] = mapped_column(Text)
    recorded_by_user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    evidence_reference: Mapped[str | None] = mapped_column(String(255))
    idempotency_key: Mapped[str | None] = mapped_column(String(120))


class DeliveryRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "delivery_records"
    transaction_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    qr_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    goat_count: Mapped[int] = mapped_column(Integer, nullable=False)
    delivery_video_evidence_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    delivery_weighment_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("weighment_sessions.id", ondelete="RESTRICT")
    )
    tolerance_result: Mapped[str | None] = mapped_column(String(30))
    recorded_by_user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    evidence_reference: Mapped[str | None] = mapped_column(String(255))
    idempotency_key: Mapped[str | None] = mapped_column(String(120))
    origin_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    final_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    difference_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    difference_percent: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    allowed_percent: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
