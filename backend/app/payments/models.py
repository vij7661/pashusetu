from uuid import UUID
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class PaymentIntent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__="payment_intents"
    transaction_id: Mapped[UUID]=mapped_column(PGUUID(as_uuid=True), ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=False, index=True)
    provider: Mapped[str]=mapped_column(String(40), nullable=False)
    provider_reference: Mapped[str|None]=mapped_column(String(120), unique=True)
    amount_paise: Mapped[int]=mapped_column(Integer, nullable=False)
    status: Mapped[str]=mapped_column(String(30), default="CREATED", nullable=False)

class PaymentWebhookEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__="payment_webhook_events"
    __table_args__=(UniqueConstraint("provider","event_key",name="uq_payment_provider_event"),)
    provider: Mapped[str]=mapped_column(String(40), nullable=False)
    event_key: Mapped[str]=mapped_column(String(160), nullable=False)
    payload_json: Mapped[str]=mapped_column(Text, nullable=False)
    status: Mapped[str]=mapped_column(String(30), default="RECEIVED", nullable=False)
