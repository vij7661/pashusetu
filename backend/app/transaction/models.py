from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Transaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "transactions"

    transaction_code: Mapped[str] = mapped_column(
        String(40), unique=True, index=True, nullable=False
    )
    listing_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("listings.id", ondelete="RESTRICT"), nullable=False
    )
    farmer_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("farmer_profiles.id", ondelete="RESTRICT"), nullable=False
    )
    buyer_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("buyer_profiles.id", ondelete="RESTRICT"), nullable=False
    )
    accepted_bid_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("bids.id", ondelete="RESTRICT"), nullable=False
    )
    state: Mapped[str] = mapped_column(String(40), default="OFFER_ACCEPTED", nullable=False)
    active_agreement_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
