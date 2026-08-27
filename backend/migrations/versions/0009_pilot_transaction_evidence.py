"""Pilot agreement snapshots and transaction evidence.

Revision ID: 0009_pilot_evidence
Revises: 0008_marketplace_partial
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009_pilot_evidence"
down_revision = "0008_marketplace_partial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("agreements", sa.Column("listing_id", postgresql.UUID(as_uuid=True)))
    op.add_column("agreements", sa.Column("farmer_profile_id", postgresql.UUID(as_uuid=True)))
    op.add_column("agreements", sa.Column("buyer_profile_id", postgresql.UUID(as_uuid=True)))
    op.add_column(
        "agreements",
        sa.Column("selected_goat_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
    )
    op.add_column("agreements", sa.Column("whole_lot", sa.Boolean()))
    op.add_column("agreements", sa.Column("accepted_price_per_kg_paise", sa.Integer()))
    op.add_column("agreements", sa.Column("agreed_weight_kg", sa.Numeric(10, 3)))
    op.add_column("agreements", sa.Column("livestock_amount_paise", sa.Integer()))
    op.create_unique_constraint(
        "uq_agreement_transaction_version", "agreements", ["transaction_id", "version"]
    )
    for table in ("pickup_records", "delivery_records"):
        op.add_column(table, sa.Column("recorded_by_user_id", postgresql.UUID(as_uuid=True)))
        op.add_column(table, sa.Column("evidence_reference", sa.String(255)))
        op.add_column(table, sa.Column("idempotency_key", sa.String(120)))
    op.add_column("delivery_records", sa.Column("origin_weight_kg", sa.Numeric(10, 3)))
    op.add_column("delivery_records", sa.Column("final_weight_kg", sa.Numeric(10, 3)))
    op.add_column("delivery_records", sa.Column("difference_kg", sa.Numeric(10, 3)))
    op.add_column("delivery_records", sa.Column("difference_percent", sa.Numeric(8, 4)))
    op.add_column("delivery_records", sa.Column("allowed_percent", sa.Numeric(8, 4)))


def downgrade() -> None:
    for column in (
        "allowed_percent",
        "difference_percent",
        "difference_kg",
        "final_weight_kg",
        "origin_weight_kg",
    ):
        op.drop_column("delivery_records", column)
    for table in ("delivery_records", "pickup_records"):
        for column in ("idempotency_key", "evidence_reference", "recorded_by_user_id"):
            op.drop_column(table, column)
    op.drop_constraint("uq_agreement_transaction_version", "agreements", type_="unique")
    for column in (
        "livestock_amount_paise",
        "agreed_weight_kg",
        "accepted_price_per_kg_paise",
        "whole_lot",
        "selected_goat_ids",
        "buyer_profile_id",
        "farmer_profile_id",
        "listing_id",
    ):
        op.drop_column("agreements", column)
