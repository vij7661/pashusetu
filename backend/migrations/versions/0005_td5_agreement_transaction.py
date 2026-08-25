"""TD-5 agreement and transaction.

Revision ID: 0005_td5
Revises: 0004_td4
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_td5"
down_revision = "0004_td4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("transaction_code", sa.String(40), nullable=False, unique=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("farmer_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmer_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("buyer_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buyer_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("accepted_bid_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bids.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("state", sa.String(40), nullable=False, server_default="OFFER_ACCEPTED"),
        sa.Column("active_agreement_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_transactions_transaction_code", "transactions", ["transaction_code"])

    op.create_table(
        "agreements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agreement_code", sa.String(40), nullable=False, unique=True),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("accepted_bid_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bids.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("price_basis", sa.String(40), nullable=False),
        sa.Column("pickup_point", sa.String(255), nullable=False),
        sa.Column("final_weighing_point", sa.String(255), nullable=False),
        sa.Column("tolerance_basis_points", sa.Integer(), nullable=False),
        sa.Column("transport_responsibility", sa.String(20), nullable=False),
        sa.Column("dispute_rule", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="PENDING_CONFIRMATION"),
        sa.Column("locked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_agreements_agreement_code", "agreements", ["agreement_code"])

    op.create_table(
        "agreement_confirmations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agreement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agreements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("party_role", sa.String(20), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("confirmed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("agreement_id", "party_role", name="uq_agreement_party_confirmation"),
    )


def downgrade() -> None:
    op.drop_table("agreement_confirmations")
    op.drop_table("agreements")
    op.drop_table("transactions")
