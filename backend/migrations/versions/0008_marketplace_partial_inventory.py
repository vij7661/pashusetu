"""Trusted marketplace coordinates and partial-lot selections.

Revision ID: 0008_marketplace_partial
Revises: 0007_td7
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0008_marketplace_partial"
down_revision = "0007_td7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("mandal_centres", sa.Column("latitude", sa.Numeric(9, 6)))
    op.add_column("mandal_centres", sa.Column("longitude", sa.Numeric(9, 6)))
    op.add_column(
        "bids",
        sa.Column(
            "selected_goat_ids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "bids", sa.Column("selected_quantity", sa.Integer(), nullable=False, server_default="1")
    )
    op.add_column("bids", sa.Column("selected_weight_kg", sa.Numeric(10, 3)))
    op.add_column(
        "bids", sa.Column("whole_lot", sa.Boolean(), nullable=False, server_default=sa.false())
    )
    op.drop_constraint("transactions_listing_id_key", "transactions", type_="unique")
    op.create_unique_constraint("uq_transaction_accepted_bid", "transactions", ["accepted_bid_id"])


def downgrade() -> None:
    op.drop_constraint("uq_transaction_accepted_bid", "transactions", type_="unique")
    op.create_unique_constraint("transactions_listing_id_key", "transactions", ["listing_id"])
    op.drop_column("bids", "whole_lot")
    op.drop_column("bids", "selected_weight_kg")
    op.drop_column("bids", "selected_quantity")
    op.drop_column("bids", "selected_goat_ids")
    op.drop_column("mandal_centres", "longitude")
    op.drop_column("mandal_centres", "latitude")
