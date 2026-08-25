"""TD-6 funds logistics delivery"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0006_td6"; down_revision="0005_td5"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("payment_intents",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("transaction_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("transactions.id",ondelete="RESTRICT"),nullable=False),
      sa.Column("provider",sa.String(40),nullable=False),sa.Column("provider_reference",sa.String(120),unique=True),sa.Column("amount_paise",sa.Integer(),nullable=False),sa.Column("status",sa.String(30),nullable=False),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("payment_webhook_events",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("provider",sa.String(40),nullable=False),sa.Column("event_key",sa.String(160),nullable=False),sa.Column("payload_json",sa.Text(),nullable=False),sa.Column("status",sa.String(30),nullable=False),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False),sa.UniqueConstraint("provider","event_key",name="uq_payment_provider_event"))
    op.create_table("transport_assignments",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("transaction_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("transactions.id",ondelete="CASCADE"),unique=True,nullable=False),
      sa.Column("transporter_name",sa.String(120),nullable=False),sa.Column("driver_name",sa.String(120),nullable=False),sa.Column("driver_phone",sa.String(30),nullable=False),sa.Column("vehicle_number",sa.String(40),nullable=False),sa.Column("status",sa.String(30),nullable=False),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("pickup_records",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("transaction_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("transactions.id",ondelete="CASCADE"),unique=True,nullable=False),sa.Column("qr_verified",sa.Boolean(),nullable=False),sa.Column("goat_count",sa.Integer(),nullable=False),sa.Column("loading_video_evidence_id",postgresql.UUID(as_uuid=True)),sa.Column("departure_note",sa.Text()),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("delivery_records",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("transaction_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("transactions.id",ondelete="CASCADE"),unique=True,nullable=False),sa.Column("qr_verified",sa.Boolean(),nullable=False),sa.Column("goat_count",sa.Integer(),nullable=False),sa.Column("delivery_video_evidence_id",postgresql.UUID(as_uuid=True)),sa.Column("delivery_weighment_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("weighment_sessions.id",ondelete="RESTRICT")),sa.Column("tolerance_result",sa.String(30)),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
def downgrade():
    op.drop_table("delivery_records");op.drop_table("pickup_records");op.drop_table("transport_assignments");op.drop_table("payment_webhook_events");op.drop_table("payment_intents")
