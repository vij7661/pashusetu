from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agreement.models import Agreement
from app.core.errors import AppError
from app.marketplace.models import Listing
from app.transaction.models import Transaction
from app.weighment.models import WeighmentSession, WeightReading


def locked_weight(db: Session, session_id):
    reading = db.scalar(
        select(WeightReading).where(
            WeightReading.weighment_session_id == session_id,
            WeightReading.locked.is_(True),
        )
    )
    if not reading:
        raise AppError("LOCKED_WEIGHT_NOT_FOUND", "Locked weight not found.", 404)
    return Decimal(reading.net_kg)


def calculate_tolerance(origin: Decimal, delivery: Decimal, basis_points: int):
    diff = abs(delivery - origin)
    percent = (diff / origin) * Decimal(100) if origin else Decimal(100)
    allowed = Decimal(basis_points) / Decimal(100)
    return diff, percent, allowed, percent <= allowed


def _listing_for_transaction(db: Session, tx: Transaction) -> Listing:
    listing = db.get(Listing, tx.listing_id)
    if listing is None:
        raise AppError("LISTING_NOT_FOUND", "Listing not found.", 404)
    return listing


def assert_delivery_weighment_matches_listing(
    delivery_session: WeighmentSession,
    listing: Listing,
) -> None:
    if (
        delivery_session.target_type != listing.target_type
        or delivery_session.target_id != listing.target_id
        or delivery_session.farmer_profile_id != listing.seller_farmer_profile_id
    ):
        raise AppError(
            "DELIVERY_WEIGHMENT_TARGET_MISMATCH",
            "Delivery weighment does not belong to the transaction listing target.",
            409,
        )


def evaluate_delivery(
    db: Session,
    tx: Transaction,
    delivery_session: WeighmentSession,
):
    if not tx.active_agreement_id:
        raise AppError("AGREEMENT_REQUIRED", "Locked agreement required.", 409)
    agreement = db.get(Agreement, tx.active_agreement_id)
    if agreement is None or not agreement.locked:
        raise AppError("AGREEMENT_REQUIRED", "Locked agreement required.", 409)

    listing = _listing_for_transaction(db, tx)
    assert_delivery_weighment_matches_listing(delivery_session, listing)
    origin = locked_weight(db, listing.weighment_session_id)
    delivery = locked_weight(db, delivery_session.id)
    diff, percent, allowed, within_tolerance = calculate_tolerance(
        origin,
        delivery,
        agreement.tolerance_basis_points,
    )
    return origin, delivery, diff, percent, allowed, within_tolerance
