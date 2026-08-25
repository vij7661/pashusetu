"""TD-7 disputes settlement audit"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision="0007_td7"; down_revision="0006_td6"; branch_labels=None; depends_on=None

def upgrade():
    op.create_table("disputes",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("dispute_code",sa.String(40),nullable=False,unique=True),
      sa.Column("transaction_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("transactions.id",ondelete="CASCADE"),nullable=False,unique=True),
      sa.Column("reason",sa.String(50),nullable=False),
      sa.Column("disputed_amount_paise",sa.Integer(),nullable=False,server_default="0"),
      sa.Column("status",sa.String(30),nullable=False,server_default="OPEN"),
      sa.Column("resolution_rule",sa.Text()),
      sa.Column("final_decision",sa.Text()),
      sa.Column("settlement_adjustment_paise",sa.Integer(),nullable=False,server_default="0"),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_disputes_dispute_code","disputes",["dispute_code"])

    op.create_table("dispute_evidence",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("dispute_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("disputes.id",ondelete="CASCADE"),nullable=False),
      sa.Column("evidence_type",sa.String(50),nullable=False),
      sa.Column("evidence_reference",sa.String(255),nullable=False),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))

    op.create_table("dispute_reweighs",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("dispute_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("disputes.id",ondelete="CASCADE"),nullable=False),
      sa.Column("weighment_session_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("weighment_sessions.id",ondelete="RESTRICT"),nullable=False),
      sa.Column("stage",sa.String(30),nullable=False),
      sa.Column("status",sa.String(30),nullable=False,server_default="RECORDED"),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))

    op.create_table("settlements",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("settlement_code",sa.String(40),nullable=False,unique=True),
      sa.Column("transaction_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("transactions.id",ondelete="CASCADE"),nullable=False,unique=True),
      sa.Column("gross_amount_paise",sa.Integer(),nullable=False),
      sa.Column("adjustment_paise",sa.Integer(),nullable=False,server_default="0"),
      sa.Column("platform_fee_paise",sa.Integer(),nullable=False,server_default="0"),
      sa.Column("final_amount_paise",sa.Integer(),nullable=False),
      sa.Column("status",sa.String(30),nullable=False,server_default="PENDING"),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_settlements_settlement_code","settlements",["settlement_code"])

    op.create_table("reputation_records",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("subject_type",sa.String(20),nullable=False),
      sa.Column("subject_id",postgresql.UUID(as_uuid=True),nullable=False),
      sa.Column("score",sa.Integer(),nullable=False,server_default="100"),
      sa.Column("completed_transactions",sa.Integer(),nullable=False,server_default="0"),
      sa.Column("disputes_opened",sa.Integer(),nullable=False,server_default="0"),
      sa.Column("disputes_lost",sa.Integer(),nullable=False,server_default="0"),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))

    op.create_table("operator_scorecards",
      sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),
      sa.Column("operator_profile_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("operator_profiles.id",ondelete="CASCADE"),nullable=False,unique=True),
      sa.Column("score",sa.Integer(),nullable=False,server_default="100"),
      sa.Column("weighment_count",sa.Integer(),nullable=False,server_default="0"),
      sa.Column("reweigh_count",sa.Integer(),nullable=False,server_default="0"),
      sa.Column("dispute_linked_count",sa.Integer(),nullable=False,server_default="0"),
      sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
      sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))

def downgrade():
    op.drop_table("operator_scorecards")
    op.drop_table("reputation_records")
    op.drop_table("settlements")
    op.drop_table("dispute_reweighs")
    op.drop_table("dispute_evidence")
    op.drop_table("disputes")
