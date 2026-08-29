from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MarketPriceRecommendation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "market_price_recommendations"

    market_code: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    breed: Mapped[str | None] = mapped_column(String(80))
    price_per_kg_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    source_label: Mapped[str] = mapped_column(String(160), nullable=False)
    valid_from: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))


class Listing(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "listings"

    listing_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    seller_farmer_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("farmer_profiles.id", ondelete="RESTRICT"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(10), nullable=False)  # GOAT / LOT
    target_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    weighment_session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("weighment_sessions.id", ondelete="RESTRICT"), nullable=False
    )
    verified_weight_kg: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    pricing_mode: Mapped[str] = mapped_column(String(20), default="PER_KG", nullable=False)
    farmer_price_per_kg_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    farmer_total_value_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("market_price_recommendations.id", ondelete="SET NULL")
    )
    farmer_acknowledged_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    farmer_acknowledgement_version: Mapped[str] = mapped_column(String(40), nullable=False)
    sale_type: Mapped[str] = mapped_column(String(30), default="COMPETITIVE_BIDDING", nullable=False)
    opens_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    closes_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    accepted_bid_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class IdempotencyRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("actor_user_id", "idempotency_key", name="uq_actor_idempotency_key"),
    )

    actor_user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(120), nullable=False)
    operation: Mapped[str] = mapped_column(String(80), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(40))
    resource_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    response_status: Mapped[int | None] = mapped_column(Integer)
    response_payload: Mapped[str | None] = mapped_column(Text)


class BidSequence(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "bid_sequences"

    listing_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    last_sequence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Bid(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "bids"
    __table_args__ = (
        UniqueConstraint("listing_id", "buyer_profile_id", "idempotency_key", name="uq_bid_intent"),
        UniqueConstraint("listing_id", "server_sequence", name="uq_listing_bid_sequence"),
    )

    bid_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    listing_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    buyer_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("buyer_profiles.id", ondelete="RESTRICT"), nullable=False
    )
    price_per_kg_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    total_offer_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(120), nullable=False)
    server_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    reject_reason: Mapped[str | None] = mapped_column(String(80))
