"""Farmer registration lifecycle and KYC pending state."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_farmer_registration"
down_revision = "0007_td7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "farmer_registrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("registration_code", sa.String(30), nullable=False, unique=True),
        sa.Column("mobile_e164", sa.String(16), nullable=False, unique=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="NEW_IN_PROGRESS"),
        sa.Column("preferred_language", sa.String(10), nullable=False, server_default="te"),
        sa.Column("full_name", sa.String(120)),
        sa.Column("village", sa.String(120)),
        sa.Column("mandal", sa.String(120)),
        sa.Column("district", sa.String(120)),
        sa.Column("state", sa.String(120), server_default="Telangana"),
        sa.Column("kyc_reference", sa.String(80), unique=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_farmer_registrations_registration_code", "farmer_registrations", ["registration_code"])
    op.create_index("ix_farmer_registrations_mobile_e164", "farmer_registrations", ["mobile_e164"])

    op.add_column("farmer_profiles", sa.Column("kyc_reference", sa.String(80), nullable=True))
    op.create_unique_constraint("uq_farmer_profiles_kyc_reference", "farmer_profiles", ["kyc_reference"])
    op.alter_column("farmer_profiles", "kyc_status", existing_type=sa.String(20), type_=sa.String(30), server_default="KYC_PENDING")


def downgrade():
    op.alter_column("farmer_profiles", "kyc_status", existing_type=sa.String(30), type_=sa.String(20), server_default="PENDING")
    op.drop_constraint("uq_farmer_profiles_kyc_reference", "farmer_profiles", type_="unique")
    op.drop_column("farmer_profiles", "kyc_reference")
    op.drop_index("ix_farmer_registrations_mobile_e164", table_name="farmer_registrations")
    op.drop_index("ix_farmer_registrations_registration_code", table_name="farmer_registrations")
    op.drop_table("farmer_registrations")
