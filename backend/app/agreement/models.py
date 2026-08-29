from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Agreement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agreements"
    __table_args__ = (
        UniqueConstraint("transaction_id", "version", name="uq_agreement_transaction_version"),
    )

    agreement_code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    transaction_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    accepted_bid_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("bids.id", ondelete="RESTRICT"), nullable=False
    )
    listing_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    farmer_profile_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    buyer_profile_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    selected_goat_ids: Mapped[list[UUID] | None] = mapped_column(ARRAY(PGUUID(as_uuid=True)))
    whole_lot: Mapped[bool | None] = mapped_column(Boolean)
    accepted_price_per_kg_paise: Mapped[int | None] = mapped_column(Integer)
    agreed_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    livestock_amount_paise: Mapped[int | None] = mapped_column(Integer)
    price_basis: Mapped[str] = mapped_column(String(40), nullable=False)
    pickup_point: Mapped[str] = mapped_column(String(255), nullable=False)
    final_weighing_point: Mapped[str] = mapped_column(String(255), nullable=False)
    tolerance_basis_points: Mapped[int] = mapped_column(Integer, nullable=False)
    transport_responsibility: Mapped[str] = mapped_column(String(20), nullable=False)
    dispute_rule: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING_CONFIRMATION", nullable=False)
    locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AgreementConfirmation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agreement_confirmations"
    __table_args__ = (
        UniqueConstraint("agreement_id", "party_role", name="uq_agreement_party_confirmation"),
    )

    agreement_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("agreements.id", ondelete="CASCADE"), nullable=False
    )
    party_role: Mapped[str] = mapped_column(String(20), nullable=False)  # FARMER / BUYER
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
