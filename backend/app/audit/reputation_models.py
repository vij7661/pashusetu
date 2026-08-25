from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ReputationRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "reputation_records"

    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)  # FARMER / BUYER
    subject_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    completed_transactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    disputes_opened: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    disputes_lost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class OperatorScorecard(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "operator_scorecards"

    operator_profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("operator_profiles.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    weighment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reweigh_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dispute_linked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
