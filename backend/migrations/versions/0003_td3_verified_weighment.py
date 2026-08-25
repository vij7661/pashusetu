"""TD-3 verified weighment.

Revision ID: 0003_td3
Revises: 0002_td2
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_td3"
down_revision = "0002_td2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mandal_centres",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("centre_code", sa.String(30), nullable=False, unique=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("village", sa.String(120)),
        sa.Column("mandal", sa.String(120)),
        sa.Column("district", sa.String(120)),
        sa.Column("state", sa.String(120), server_default="Telangana"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_mandal_centres_centre_code", "mandal_centres", ["centre_code"])

    op.create_table(
        "operator_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("operator_code", sa.String(30), nullable=False, unique=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("centre_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mandal_centres.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_operator_profiles_operator_code", "operator_profiles", ["operator_code"])

    op.create_table(
        "scale_devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scale_code", sa.String(40), nullable=False, unique=True),
        sa.Column("centre_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mandal_centres.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("vendor", sa.String(120)),
        sa.Column("model", sa.String(120)),
        sa.Column("bluetooth_identifier", sa.String(160)),
        sa.Column("calibration_status", sa.String(30), nullable=False, server_default="VALID"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_scale_devices_scale_code", "scale_devices", ["scale_code"])

    op.create_table(
        "weighment_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("weighment_code", sa.String(40), nullable=False, unique=True),
        sa.Column("target_type", sa.String(10), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmer_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("operator_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("centre_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mandal_centres.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("scale_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scale_devices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="LIVE"),
        sa.Column("reweigh_of_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("weighment_sessions.id", ondelete="RESTRICT")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("target_type IN ('GOAT','LOT')", name="ck_weighment_target_type"),
    )
    op.create_index("ix_weighment_sessions_weighment_code", "weighment_sessions", ["weighment_code"])
    op.create_index("ix_weighment_sessions_target_id", "weighment_sessions", ["target_id"])

    op.create_table(
        "weight_readings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("weighment_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("weighment_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column("gross_kg", sa.Numeric(10, 3), nullable=False),
        sa.Column("tare_kg", sa.Numeric(10, 3), nullable=False),
        sa.Column("net_kg", sa.Numeric(10, 3), nullable=False),
        sa.Column("stable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("locked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_weight_readings_weighment_session_id", "weight_readings", ["weighment_session_id"])

    op.create_table(
        "farmer_weighment_acknowledgements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("weighment_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("weighment_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("farmer_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmer_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("method", sa.String(30), nullable=False, server_default="APP_CONFIRMATION"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("weighment_session_id", name="uq_weighment_ack"),
    )

    op.create_table(
        "weighment_receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("weighment_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("weighment_sessions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("receipt_code", sa.String(40), nullable=False, unique=True),
        sa.Column("qr_payload", sa.Text(), nullable=False),
        sa.Column("print_status", sa.String(30), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_weighment_receipts_receipt_code", "weighment_receipts", ["receipt_code"])


def downgrade() -> None:
    op.drop_table("weighment_receipts")
    op.drop_table("farmer_weighment_acknowledgements")
    op.drop_table("weight_readings")
    op.drop_table("weighment_sessions")
    op.drop_table("scale_devices")
    op.drop_table("operator_profiles")
    op.drop_table("mandal_centres")
