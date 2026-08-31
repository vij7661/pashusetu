from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agreement.models import Agreement
from app.core.errors import AppError
from app.transaction.models import Transaction
from app.weighment.models import WeighmentSession, WeightReading


def locked_weight(db, session_id):
    r = db.scalar(
        select(WeightReading).where(
            WeightReading.weighment_session_id == session_id,
            WeightReading.locked.is_(True),
        )
    )
    if not r:
        raise AppError("LOCKED_WEIGHT_NOT_FOUND", "Locked weight not found.", 404)
    return Decimal(r.net_kg)


def calculate_tolerance(origin: Decimal, delivery: Decimal, basis_points: int):
    diff = abs(delivery - origin)
    pct = (diff / origin) * Decimal("100") if origin else Decimal("100")
    allowed = Decimal(basis_points) / Decimal("100")
    return diff, pct, allowed, pct <= allowed


def evaluate_delivery(db: Session, tx: Transaction, delivery_session: WeighmentSession):
    if not tx.active_agreement_id:
        raise AppError("AGREEMENT_REQUIRED", "Locked agreement required.", 409)
    agreement = db.get(Agreement, tx.active_agreement_id)
    listing_model = __import__("app.marketplace.models", fromlist=["Listing"]).Listing
    origin_session_id = db.scalar(
        select(listing_model.weighment_session_id).where(listing_model.id == tx.listing_id)
    )
    origin = locked_weight(db, origin_session_id)
    delivery = locked_weight(db, delivery_session.id)
    diff, pct, allowed, ok = calculate_tolerance(
        origin,
        delivery,
        agreement.tolerance_basis_points,
    )
    return origin, delivery, diff, pct, allowed, ok
