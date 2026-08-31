"""Seed cross-role transaction states needed to manually QA the Farmer UI.

Development/test only. These records are controlled fixtures, not production behavior.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.auth.service import DEVELOPMENT_ENVS
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.identity.profile_models import BuyerProfile, FarmerProfile
from app.livestock.models import Goat
from app.marketplace.models import Bid, BidSequence, Listing
from app.transaction.models import Transaction
from app.weighment.models import WeighmentSession

FARMER_CODE = "F-FV2-033"
BUYER_CODE = "PS-B-QA001"
TARGET_CODE = "GOAT-QA-CREATE"


def _ensure_state_transaction(db, *, suffix: str, state: str, farmer, buyer, goat, weighment):
    transaction_code = f"TX-QA-{suffix}"
    existing = db.scalar(
        select(Transaction).where(Transaction.transaction_code == transaction_code)
    )
    if existing is not None:
        return existing

    now = datetime.now(UTC)
    listing = Listing(
        listing_code=f"PS-LST-QA-{suffix}",
        seller_farmer_profile_id=farmer.id,
        target_type="GOAT",
        target_id=goat.id,
        weighment_session_id=weighment.id,
        verified_weight_kg=Decimal("50.000"),
        farmer_price_per_kg_paise=40000,
        farmer_total_value_paise=2_000_000,
        sale_type="COMPETITIVE_BIDDING",
        opens_at=now - timedelta(days=1),
        closes_at=now + timedelta(days=7),
        status="OFFER_ACCEPTED",
    )
    db.add(listing)
    db.flush()

    bid = Bid(
        bid_code=f"BID-QA-{suffix}",
        listing_id=listing.id,
        buyer_profile_id=buyer.id,
        price_per_kg_paise=42000,
        total_offer_paise=2_100_000,
        idempotency_key=f"farmer-manual-qa-{suffix.lower()}",
        server_sequence=1,
        status="ACCEPTED",
    )
    db.add(bid)
    db.flush()
    db.add(BidSequence(listing_id=listing.id, last_sequence=1))
    listing.accepted_bid_id = bid.id

    tx = Transaction(
        transaction_code=transaction_code,
        listing_id=listing.id,
        farmer_profile_id=farmer.id,
        buyer_profile_id=buyer.id,
        accepted_bid_id=bid.id,
        state=state,
    )
    db.add(tx)
    db.flush()
    return tx


def seed_states():
    settings = get_settings()
    if settings.app_env.lower() not in DEVELOPMENT_ENVS:
        raise RuntimeError(
            "Farmer manual-QA state fixtures are forbidden outside local/test/development."
        )

    db = SessionLocal()
    try:
        farmer = db.scalar(
            select(FarmerProfile).where(FarmerProfile.farmer_code == FARMER_CODE)
        )
        buyer = db.scalar(select(BuyerProfile).where(BuyerProfile.buyer_code == BUYER_CODE))
        goat = db.scalar(select(Goat).where(Goat.goat_code == TARGET_CODE))
        if farmer is None or buyer is None or goat is None:
            raise RuntimeError(
                "Run scripts/seed_farmer_manual_qa.py before state fixtures."
            )
        weighment = db.scalar(
            select(WeighmentSession).where(
                WeighmentSession.target_type == "GOAT",
                WeighmentSession.target_id == goat.id,
                WeighmentSession.status == "VERIFIED",
            )
        )
        if weighment is None:
            raise RuntimeError("Verified QA weighment is missing.")

        _ensure_state_transaction(
            db,
            suffix="SHIPMENT",
            state="IN_TRANSIT",
            farmer=farmer,
            buyer=buyer,
            goat=goat,
            weighment=weighment,
        )
        _ensure_state_transaction(
            db,
            suffix="DISPUTED",
            state="DISPUTED",
            farmer=farmer,
            buyer=buyer,
            goat=goat,
            weighment=weighment,
        )
        _ensure_state_transaction(
            db,
            suffix="SETTLED",
            state="SETTLED",
            farmer=farmer,
            buyer=buyer,
            goat=goat,
            weighment=weighment,
        )
        db.commit()
        print("Farmer transaction-state fixtures ready")
        print("TX-QA-SHIPMENT -> IN_TRANSIT")
        print("TX-QA-DISPUTED -> DISPUTED")
        print("TX-QA-SETTLED -> SETTLED")
    finally:
        db.close()


if __name__ == "__main__":
    seed_states()
