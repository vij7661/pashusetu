"""Persist Farmer acknowledgement evidence on listings."""

from alembic import op
import sqlalchemy as sa

revision = "0009_listing_ack"
down_revision = "0008_farmer_registration"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "listings",
        sa.Column("farmer_acknowledged_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "listings",
        sa.Column("farmer_acknowledgement_version", sa.String(40), nullable=True),
    )


def downgrade():
    op.drop_column("listings", "farmer_acknowledgement_version")
    op.drop_column("listings", "farmer_acknowledged_at")
