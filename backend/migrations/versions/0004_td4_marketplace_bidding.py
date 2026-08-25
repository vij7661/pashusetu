"""TD-4 marketplace and bidding.

Revision ID: 0004_td4
Revises: 0003_td3
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_td4"
down_revision = "0003_td3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "market_price_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("market_code", sa.String(40), nullable=False),
        sa.Column("breed", sa.String(80)),
        sa.Column("price_per_kg_paise", sa.Integer(), nullable=False),
        sa.Column("source_label", sa.String(160), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_to", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_market_price_recommendations_market_code", "market_price_recommendations", ["market_code"])

    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("listing_code", sa.String(40), nullable=False, unique=True),
        sa.Column("seller_farmer_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmer_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("target_type", sa.String(10), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("weighment_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("weighment_sessions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("verified_weight_kg", sa.Numeric(10, 3), nullable=False),
        sa.Column("pricing_mode", sa.String(20), nullable=False, server_default="PER_KG"),
        sa.Column("farmer_price_per_kg_paise", sa.Integer(), nullable=False),
        sa.Column("farmer_total_value_paise", sa.Integer(), nullable=False),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("market_price_recommendations.id", ondelete="SET NULL")),
        sa.Column("sale_type", sa.String(30), nullable=False, server_default="COMPETITIVE_BIDDING"),
        sa.Column("opens_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closes_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="DRAFT"),
        sa.Column("accepted_bid_id", postgresql.UUID(as_uuid=True)),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_listings_listing_code", "listings", ["listing_code"])
    op.create_index("ix_listings_target_id", "listings", ["target_id"])

    op.create_table(
        "idempotency_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", sa.String(120), nullable=False),
        sa.Column("operation", sa.String(80), nullable=False),
        sa.Column("request_fingerprint", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.String(40)),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True)),
        sa.Column("response_status", sa.Integer()),
        sa.Column("response_payload", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("actor_user_id", "idempotency_key", name="uq_actor_idempotency_key"),
    )
    op.create_index("ix_idempotency_records_actor_user_id", "idempotency_records", ["actor_user_id"])

    op.create_table(
        "bid_sequences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("last_sequence", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "bids",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bid_code", sa.String(40), nullable=False, unique=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("buyer_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buyer_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("price_per_kg_paise", sa.Integer(), nullable=False),
        sa.Column("total_offer_paise", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(120), nullable=False),
        sa.Column("server_sequence", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="ACTIVE"),
        sa.Column("reject_reason", sa.String(80)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("listing_id", "buyer_profile_id", "idempotency_key", name="uq_bid_intent"),
        sa.UniqueConstraint("listing_id", "server_sequence", name="uq_listing_bid_sequence"),
    )
    op.create_index("ix_bids_bid_code", "bids", ["bid_code"])
    op.create_index("ix_bids_listing_id", "bids", ["listing_id"])


def downgrade() -> None:
    op.drop_table("bids")
    op.drop_table("bid_sequences")
    op.drop_table("idempotency_records")
    op.drop_table("listings")
    op.drop_table("market_price_recommendations")
