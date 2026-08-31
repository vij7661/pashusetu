from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.service import append_event
from app.core.errors import AppError
from app.identity.profile_models import FarmerProfile
from app.livestock.models import Goat, Lot
from app.marketplace.models import Listing, MarketPriceRecommendation
from app.weighment.models import WeighmentSession, WeightReading

PILOT_MARKET_CODE = "HYDERABAD"
FARMER_ACKNOWLEDGEMENT_VERSION = "VERIFIED_WEIGHMENT_V1"


def _farmer_for_user(db: Session, user_id: UUID) -> FarmerProfile:
    farmer = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user_id))
    if not farmer:
        raise AppError("FARMER_PROFILE_REQUIRED", "Farmer profile is required.", 409)
    return farmer


def _target_for_farmer(db: Session, farmer: FarmerProfile, target_type: str, target_code: str):
    if target_type == "GOAT":
        target = db.scalar(
            select(Goat).where(
                Goat.goat_code == target_code,
                Goat.farmer_profile_id == farmer.id,
            )
        )
    else:
        target = db.scalar(
            select(Lot).where(
                Lot.lot_code == target_code,
                Lot.farmer_profile_id == farmer.id,
            )
        )
    if not target:
        raise AppError("LISTING_TARGET_NOT_FOUND", "Goat or lot not found.", 404)
    return target


def _verified_weighment(db: Session, target_type: str, target_id: UUID) -> tuple[WeighmentSession, Decimal]:
    session = db.scalar(
        select(WeighmentSession)
        .where(
            WeighmentSession.target_type == target_type,
            WeighmentSession.target_id == target_id,
            WeighmentSession.status == "VERIFIED",
        )
        .order_by(WeighmentSession.created_at.desc())
    )
    if not session:
        raise AppError("VERIFIED_WEIGHMENT_REQUIRED", "Verified weighment is required before listing.", 409)

    reading = db.scalar(
        select(WeightReading).where(
            WeightReading.weighment_session_id == session.id,
            WeightReading.locked.is_(True),
        )
    )
    if not reading:
        raise AppError("LOCKED_READING_REQUIRED", "Locked weighment reading not found.", 500)
    return session, reading.net_kg


def get_listing_context(
    db: Session,
    user_id: UUID,
    target_type: str,
    target_code: str,
) -> tuple[Decimal, str]:
    farmer = _farmer_for_user(db, user_id)
    target = _target_for_farmer(db, farmer, target_type, target_code)
    _, verified_weight = _verified_weighment(db, target_type, target.id)
    return verified_weight, PILOT_MARKET_CODE


def calculate_total_paise(weight_kg: Decimal, price_per_kg_paise: int) -> int:
    total = weight_kg * Decimal(price_per_kg_paise)
    return int(total.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _validate_reference_window(valid_from: datetime, valid_to: datetime | None) -> None:
    if valid_to is not None and valid_to <= valid_from:
        raise AppError("INVALID_REFERENCE_WINDOW", "Reference price expiry must be after its start.", 400)


def create_market_reference(
    db: Session,
    market_code: str,
    breed: str | None,
    price_per_kg_paise: int,
    source_label: str,
    valid_from: datetime,
    valid_to: datetime | None,
    actor_user_id: UUID | None = None,
) -> MarketPriceRecommendation:
    _validate_reference_window(valid_from, valid_to)
    reference = MarketPriceRecommendation(
        market_code=market_code.strip().upper(),
        breed=breed.strip() if breed else None,
        price_per_kg_paise=price_per_kg_paise,
        source_label=source_label.strip(),
        valid_from=valid_from,
        valid_to=valid_to,
    )
    db.add(reference)
    db.flush()
    append_event(
        db,
        "MARKET_REFERENCE",
        reference.id,
        "MARKET_REFERENCE_CREATED",
        actor_user_id=actor_user_id,
        payload={
            "market_code": reference.market_code,
            "breed": reference.breed,
            "price_per_kg_paise": reference.price_per_kg_paise,
            "source_label": reference.source_label,
            "valid_from": reference.valid_from.isoformat(),
            "valid_to": reference.valid_to.isoformat() if reference.valid_to else None,
        },
        commit=False,
    )
    db.commit()
    db.refresh(reference)
    return reference


def version_market_reference(
    db: Session,
    recommendation_id: UUID,
    effective_from: datetime,
    valid_to: datetime | None,
    market_code: str,
    breed: str | None,
    price_per_kg_paise: int,
    source_label: str,
    actor_user_id: UUID | None = None,
) -> MarketPriceRecommendation:
    current = db.get(MarketPriceRecommendation, recommendation_id)
    if current is None:
        raise AppError("RECOMMENDATION_NOT_FOUND", "Market reference price not found.", 404)
    if effective_from <= current.valid_from:
        raise AppError(
            "INVALID_REFERENCE_VERSION_TIME",
            "Edited reference must become effective after the original reference start.",
            400,
        )
    _validate_reference_window(effective_from, valid_to)

    current.valid_to = effective_from
    replacement = MarketPriceRecommendation(
        market_code=market_code.strip().upper(),
        breed=breed.strip() if breed else None,
        price_per_kg_paise=price_per_kg_paise,
        source_label=source_label.strip(),
        valid_from=effective_from,
        valid_to=valid_to,
    )
    db.add(replacement)
    db.flush()
    append_event(
        db,
        "MARKET_REFERENCE",
        current.id,
        "MARKET_REFERENCE_SUPERSEDED",
        actor_user_id=actor_user_id,
        payload={
            "replacement_reference_id": str(replacement.id),
            "effective_from": effective_from.isoformat(),
        },
        commit=False,
    )
    append_event(
        db,
        "MARKET_REFERENCE",
        replacement.id,
        "MARKET_REFERENCE_VERSION_CREATED",
        actor_user_id=actor_user_id,
        payload={
            "previous_reference_id": str(current.id),
            "market_code": replacement.market_code,
            "breed": replacement.breed,
            "price_per_kg_paise": replacement.price_per_kg_paise,
            "source_label": replacement.source_label,
            "valid_from": replacement.valid_from.isoformat(),
            "valid_to": replacement.valid_to.isoformat() if replacement.valid_to else None,
        },
        commit=False,
    )
    db.commit()
    db.refresh(replacement)
    return replacement


def create_listing(
    db: Session,
    user_id: UUID,
    target_type: str,
    target_code: str,
    farmer_price_per_kg_paise: int,
    farmer_acknowledged: bool,
    sale_type: str,
    opens_at,
    closes_at,
    recommendation_id: UUID | None = None,
) -> Listing:
    if not farmer_acknowledged:
        raise AppError(
            "FARMER_ACKNOWLEDGEMENT_REQUIRED",
            "Farmer acknowledgement is required before publishing a listing.",
            400,
        )
    if closes_at <= opens_at:
        raise AppError("INVALID_LISTING_WINDOW", "Listing close must be after open.", 400)

    farmer = _farmer_for_user(db, user_id)
    target = _target_for_farmer(db, farmer, target_type, target_code)
    session, verified_weight = _verified_weighment(db, target_type, target.id)
    acknowledged_at = datetime.now(UTC)

    if recommendation_id:
        recommendation = db.get(MarketPriceRecommendation, recommendation_id)
        if not recommendation:
            raise AppError("RECOMMENDATION_NOT_FOUND", "Market reference price not found.", 404)
        if recommendation.market_code != PILOT_MARKET_CODE:
            raise AppError(
                "REFERENCE_MARKET_MISMATCH",
                "Selected reference price does not belong to the listing market.",
                409,
            )
        if recommendation.valid_from > acknowledged_at or (
            recommendation.valid_to is not None and recommendation.valid_to <= acknowledged_at
        ):
            raise AppError(
                "REFERENCE_PRICE_NOT_ACTIVE",
                "Selected reference price is no longer active. Reload the current reference price.",
                409,
            )

    listing = Listing(
        listing_code=f"PS-LST-{uuid4().hex[:10].upper()}",
        seller_farmer_profile_id=farmer.id,
        target_type=target_type,
        target_id=target.id,
        weighment_session_id=session.id,
        verified_weight_kg=verified_weight,
        farmer_price_per_kg_paise=farmer_price_per_kg_paise,
        farmer_total_value_paise=calculate_total_paise(verified_weight, farmer_price_per_kg_paise),
        recommendation_id=recommendation_id,
        farmer_acknowledged_at=acknowledged_at,
        farmer_acknowledgement_version=FARMER_ACKNOWLEDGEMENT_VERSION,
        sale_type=sale_type,
        opens_at=opens_at,
        closes_at=closes_at,
        status="PUBLISHED",
    )
    db.add(listing)
    db.flush()
    append_event(
        db,
        "LISTING",
        listing.id,
        "LISTING_PUBLISHED",
        actor_user_id=user_id,
        payload={
            "listing_code": listing.listing_code,
            "target_type": target_type,
            "target_id": str(target.id),
            "weighment_session_id": str(session.id),
            "verified_weight_kg": str(verified_weight),
            "farmer_price_per_kg_paise": farmer_price_per_kg_paise,
            "farmer_total_value_paise": listing.farmer_total_value_paise,
            "recommendation_id": str(recommendation_id) if recommendation_id else None,
            "farmer_acknowledged_at": acknowledged_at.isoformat(),
            "farmer_acknowledgement_version": FARMER_ACKNOWLEDGEMENT_VERSION,
        },
        commit=False,
    )
    db.commit()
    db.refresh(listing)
    return listing


def close_listing_if_expired(db: Session, listing: Listing) -> Listing:
    now = datetime.now(UTC)
    if listing.status == "PUBLISHED" and now >= listing.closes_at:
        listing.status = "CLOSED"
        db.commit()
        db.refresh(listing)
    return listing
