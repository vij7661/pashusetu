from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Dispute(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "disputes"

    dispute_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    transaction_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    disputed_amount_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False)
    resolution_rule: Mapped[str | None] = mapped_column(Text)
    final_decision: Mapped[str | None] = mapped_column(Text)
    settlement_adjustment_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class DisputeEvidence(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "dispute_evidence"

    dispute_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence_reference: Mapped[str] = mapped_column(String(255), nullable=False)


class DisputeReweigh(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "dispute_reweighs"

    dispute_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False
    )
    weighment_session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("weighment_sessions.id", ondelete="RESTRICT"), nullable=False
    )
    stage: Mapped[str] = mapped_column(String(30), nullable=False)  # CONTROLLED / INDEPENDENT
    status: Mapped[str] = mapped_column(String(30), default="RECORDED", nullable=False)


class Settlement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "settlements"

    settlement_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    transaction_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    gross_amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    adjustment_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    platform_fee_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    final_amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
