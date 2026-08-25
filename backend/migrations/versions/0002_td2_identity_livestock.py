"""TD-2 identity profiles, livestock and evidence.

Revision ID: 0002_td2
Revises: 0001_td1
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_td2"
down_revision = "0001_td1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "farmer_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("farmer_code", sa.String(30), nullable=False, unique=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("village", sa.String(120)),
        sa.Column("mandal", sa.String(120)),
        sa.Column("district", sa.String(120)),
        sa.Column("state", sa.String(120)),
        sa.Column("latitude", sa.String(32)),
        sa.Column("longitude", sa.String(32)),
        sa.Column("kyc_status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("payout_status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_farmer_profiles_farmer_code", "farmer_profiles", ["farmer_code"])

    op.create_table(
        "buyer_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("buyer_code", sa.String(30), nullable=False, unique=True),
        sa.Column("business_name", sa.String(160), nullable=False),
        sa.Column("contact_person", sa.String(120)),
        sa.Column("buyer_type", sa.String(40), nullable=False),
        sa.Column("city", sa.String(120)),
        sa.Column("state", sa.String(120)),
        sa.Column("latitude", sa.String(32)),
        sa.Column("longitude", sa.String(32)),
        sa.Column("kyc_status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("business_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_buyer_profiles_buyer_code", "buyer_profiles", ["buyer_code"])

    op.create_table(
        "goats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("goat_code", sa.String(30), nullable=False, unique=True),
        sa.Column("farmer_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmer_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("breed", sa.String(80)),
        sa.Column("sex", sa.String(10)),
        sa.Column("age_months", sa.Integer()),
        sa.Column("health_notes", sa.Text()),
        sa.Column("status", sa.String(30), nullable=False, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_goats_goat_code", "goats", ["goat_code"])

    op.create_table(
        "lots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lot_code", sa.String(30), nullable=False, unique=True),
        sa.Column("farmer_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmer_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("declared_quantity", sa.Integer(), nullable=False),
        sa.Column("breed_summary", sa.String(160)),
        sa.Column("sex_summary", sa.String(160)),
        sa.Column("age_summary", sa.String(160)),
        sa.Column("health_notes", sa.Text()),
        sa.Column("status", sa.String(30), nullable=False, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("declared_quantity > 0", name="ck_lot_quantity_positive"),
    )
    op.create_index("ix_lots_lot_code", "lots", ["lot_code"])

    op.create_table(
        "lot_goats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("goat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("goats.id", ondelete="CASCADE"), nullable=False, unique=True),
    )

    op.create_table(
        "evidence_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_type", sa.String(30), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_type", sa.String(40), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("sha256_hex", sa.String(64)),
        sa.Column("captured_by_user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("status", sa.String(20), nullable=False, server_default="UPLOADED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_evidence_assets_owner_type", "evidence_assets", ["owner_type"])
    op.create_index("ix_evidence_assets_owner_id", "evidence_assets", ["owner_id"])


def downgrade() -> None:
    op.drop_table("evidence_assets")
    op.drop_table("lot_goats")
    op.drop_table("lots")
    op.drop_table("goats")
    op.drop_table("buyer_profiles")
    op.drop_table("farmer_profiles")
