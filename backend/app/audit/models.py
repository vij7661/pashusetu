from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, JSON, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin


class AuditEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "audit_events"
    __table_args__ = (
        UniqueConstraint("aggregate_type", "aggregate_id", "sequence", name="uq_event_sequence"),
    )

    aggregate_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    aggregate_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(BigInteger, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    actor_user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    request_id: Mapped[str | None] = mapped_column(String(80))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
