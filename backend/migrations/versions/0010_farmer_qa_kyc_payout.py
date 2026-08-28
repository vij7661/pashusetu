"""Masked Farmer KYC and payout setup state.

Revision ID: 0010_farmer_kyc_payout
Revises: 0009_pilot_evidence
"""

import sqlalchemy as sa
from alembic import op

revision = "0010_farmer_kyc_payout"
down_revision = "0009_pilot_evidence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("farmer_profiles", sa.Column("kyc_masked_id", sa.String(20)))
    op.add_column("farmer_profiles", sa.Column("kyc_provider_reference", sa.String(80)))
    op.add_column("farmer_profiles", sa.Column("payout_method", sa.String(20)))
    op.add_column("farmer_profiles", sa.Column("payout_masked_reference", sa.String(120)))


def downgrade() -> None:
    for column in ("payout_masked_reference", "payout_method", "kyc_provider_reference", "kyc_masked_id"):
        op.drop_column("farmer_profiles", column)
