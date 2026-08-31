"""Seed deterministic Farmer manual-QA scenarios for local/development only.

This script deliberately creates controlled development data directly in the database.
It never stores raw Aadhaar and refuses to run outside local/test/development.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.auth.service import DEVELOPMENT_ENVS, _development_otp
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.identity.models import User, UserRole
from app.identity.profile_models import BuyerProfile, FarmerProfile, FarmerRegistration
from app.livestock.models import Goat
from app.marketplace.models import Bid, BidSequence, Listing, MarketPriceRecommendation
from app.weighment.models import (
    FarmerWeighmentAcknowledgement,
    MandalCentre,
    OperatorProfile,
    ScaleDevice,
    WeighmentReceipt,
    WeighmentSession,
    WeightReading,
)

FRESH_MOBILE = "+919100000001"
IN_PROGRESS_MOBILE = "+919100000017"
KYC_PENDING_MOBILE = "+919100000025"
VERIFIED_MOBILE = "+919100000033"
BUYER_MOBILE = "+919100009001"
OPERATOR_MOBILE = "+919100009002"


def _ensure_user(db, mobile: str, language: str, role: str) -> User:
    user = db.scalar(select(User).where(User.mobile_e164 == mobile))
    if user is None:
        user = User(
            mobile_e164=mobile,
            preferred_language=language,
            status="ACTIVE",
        )
        db.add(user)
        db.flush()
    role_row = db.scalar(
        select(UserRole).where(UserRole.user_id == user.id, UserRole.role == role)
    )
    if role_row is None:
        db.add(UserRole(user_id=user.id, role=role))
        db.flush()
    return user


def _ensure_registration(
    db,
    *,
    mobile: str,
    code: str,
    language: str,
    full_name: str | None,
    status: str,
    user_id=None,
    kyc_reference: str | None = None,
):
    registration = db.scalar(
        select(FarmerRegistration).where(FarmerRegistration.mobile_e164 == mobile)
    )
    if registration is None:
        registration = FarmerRegistration(
            registration_code=code,
            mobile_e164=mobile,
            status=status,
            preferred_language=language,
            full_name=full_name,
            village="Chityal" if full_name else None,
            mandal="Chityal" if full_name else None,
            district="Nalgonda" if full_name else None,
            state="Telangana" if full_name else None,
            user_id=user_id,
            kyc_reference=kyc_reference,
        )
        db.add(registration)
        db.flush()
    return registration


def _ensure_farmer_profile(
    db,
    *,
    user: User,
    code: str,
    name: str,
    kyc_status: str,
    kyc_reference: str,
) -> FarmerProfile:
    profile = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    if profile is None:
        profile = FarmerProfile(
            user_id=user.id,
            farmer_code=code,
            full_name=name,
            village="Chityal",
            mandal="Chityal",
            district="Nalgonda",
            state="Telangana",
            kyc_status=kyc_status,
            kyc_reference=kyc_reference,
            payout_status="VERIFIED" if kyc_status == "KYC_VERIFIED" else "PENDING",
        )
        db.add(profile)
        db.flush()
    return profile


def _ensure_qa_infrastructure(db):
    centre = db.scalar(select(MandalCentre).where(MandalCentre.centre_code == "QA-CHY-01"))
    if centre is None:
        centre = MandalCentre(
            centre_code="QA-CHY-01",
            name="Farmer QA Chityal Centre",
            village="Chityal",
            mandal="Chityal",
            district="Nalgonda",
            state="Telangana",
        )
        db.add(centre)
        db.flush()

    operator_user = _ensure_user(db, OPERATOR_MOBILE, "en", "OPERATOR")
    operator = db.scalar(
        select(OperatorProfile).where(OperatorProfile.user_id == operator_user.id)
    )
    if operator is None:
        operator = OperatorProfile(
            user_id=operator_user.id,
            operator_code="OP-QA-001",
            full_name="QA Operator",
            centre_id=centre.id,
            active=True,
        )
        db.add(operator)
        db.flush()

    scale = db.scalar(select(ScaleDevice).where(ScaleDevice.scale_code == "QA-SCALE-01"))
    if scale is None:
        scale = ScaleDevice(
            scale_code="QA-SCALE-01",
            centre_id=centre.id,
            vendor="SIMULATED",
            model="QA-DEV-SCALE",
            bluetooth_identifier="QA-BT-SCALE-01",
            calibration_status="VALID",
            active=True,
        )
        db.add(scale)
        db.flush()

    return centre, operator, scale


def _ensure_buyer(db) -> BuyerProfile:
    user = _ensure_user(db, BUYER_MOBILE, "en", "BUYER")
    buyer = db.scalar(select(BuyerProfile).where(BuyerProfile.user_id == user.id))
    if buyer is None:
        buyer = BuyerProfile(
            user_id=user.id,
            buyer_code="PS-B-QA001",
            business_name="QA Hyderabad Buyer",
            contact_person="QA Buyer",
            buyer_type="BULK_BUYER",
            city="Hyderabad",
            state="Telangana",
            kyc_status="VERIFIED",
            business_verified=True,
        )
        db.add(buyer)
        db.flush()
    return buyer


def _ensure_verified_goat(db, farmer, operator, centre, scale, *, code: str, weight: Decimal):
    goat = db.scalar(select(Goat).where(Goat.goat_code == code))
    if goat is None:
        goat = Goat(
            goat_code=code,
            farmer_profile_id=farmer.id,
            breed="Sirohi",
            sex="MALE",
            age_months=18,
            status="VERIFIED",
        )
        db.add(goat)
        db.flush()

    weighment = db.scalar(
        select(WeighmentSession).where(WeighmentSession.weighment_code == f"WG-{code}")
    )
    if weighment is None:
        weighment = WeighmentSession(
            weighment_code=f"WG-{code}",
            target_type="GOAT",
            target_id=goat.id,
            farmer_profile_id=farmer.id,
            operator_id=operator.id,
            centre_id=centre.id,
            scale_id=scale.id,
            status="VERIFIED",
        )
        db.add(weighment)
        db.flush()
        db.add(
            WeightReading(
                weighment_session_id=weighment.id,
                sequence_no=1,
                gross_kg=weight,
                tare_kg=Decimal("0.000"),
                net_kg=weight,
                stable=True,
                locked=True,
            )
        )
        db.add(
            FarmerWeighmentAcknowledgement(
                weighment_session_id=weighment.id,
                farmer_profile_id=farmer.id,
                acknowledged=True,
                method="APP_CONFIRMATION",
            )
        )
        db.add(
            WeighmentReceipt(
                weighment_session_id=weighment.id,
                receipt_code=f"RCPT-{code}",
                qr_payload=f"pashusetu://qa/weighment/{weighment.weighment_code}",
                print_status="READY",
            )
        )
        db.flush()
    return goat, weighment


def _ensure_market_recommendation(db):
    row = db.scalar(
        select(MarketPriceRecommendation).where(
            MarketPriceRecommendation.market_code == "HYDERABAD",
            MarketPriceRecommendation.source_label == "Farmer Manual QA",
        )
    )
    if row is None:
        now = datetime.now(UTC)
        row = MarketPriceRecommendation(
            market_code="HYDERABAD",
            breed="Sirohi",
            price_per_kg_paise=40000,
            source_label="Farmer Manual QA",
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=30),
        )
        db.add(row)
        db.flush()
    return row


def _ensure_listing_with_offer(db, farmer, goat, weighment, recommendation, buyer):
    listing = db.scalar(select(Listing).where(Listing.listing_code == "PS-LST-QA-OFFER"))
    if listing is None:
        now = datetime.now(UTC)
        listing = Listing(
            listing_code="PS-LST-QA-OFFER",
            seller_farmer_profile_id=farmer.id,
            target_type="GOAT",
            target_id=goat.id,
            weighment_session_id=weighment.id,
            verified_weight_kg=Decimal("48.500"),
            farmer_price_per_kg_paise=40000,
            farmer_total_value_paise=1_940_000,
            recommendation_id=recommendation.id,
            sale_type="COMPETITIVE_BIDDING",
            opens_at=now - timedelta(hours=1),
            closes_at=now + timedelta(days=7),
            status="PUBLISHED",
        )
        db.add(listing)
        db.flush()

    bid = db.scalar(select(Bid).where(Bid.bid_code == "BID-QA-001"))
    if bid is None:
        bid = Bid(
            bid_code="BID-QA-001",
            listing_id=listing.id,
            buyer_profile_id=buyer.id,
            price_per_kg_paise=42000,
            total_offer_paise=2_037_000,
            idempotency_key="farmer-manual-qa-offer-001",
            server_sequence=1,
            status="ACTIVE",
        )
        db.add(bid)
        db.add(BidSequence(listing_id=listing.id, last_sequence=1))
        db.flush()
    return listing, bid


def seed():
    settings = get_settings()
    if settings.app_env.lower() not in DEVELOPMENT_ENVS:
        raise RuntimeError(
            "Farmer manual-QA fixtures are forbidden outside local/test/development."
        )

    db = SessionLocal()
    try:
        # FV2-001 intentionally remains absent: using it exercises a brand-new registration.
        existing_fresh = db.scalar(select(User).where(User.mobile_e164 == FRESH_MOBILE))
        existing_fresh_registration = db.scalar(
            select(FarmerRegistration).where(FarmerRegistration.mobile_e164 == FRESH_MOBILE)
        )
        if existing_fresh or existing_fresh_registration:
            raise RuntimeError(
                f"{FRESH_MOBILE} is reserved for the fresh-registration scenario. "
                "Reset the QA database with `docker compose down -v` before reseeding."
            )

        _ensure_registration(
            db,
            mobile=IN_PROGRESS_MOBILE,
            code="REG-FV2-017",
            language="te",
            full_name="Shankar QA Farmer",
            status="NEW_IN_PROGRESS",
        )

        pending_user = _ensure_user(db, KYC_PENDING_MOBILE, "te", "FARMER")
        pending_reference = "KYC-QA-PENDING-025"
        _ensure_farmer_profile(
            db,
            user=pending_user,
            code="F-FV2-025",
            name="QA Pending Farmer",
            kyc_status="KYC_PENDING",
            kyc_reference=pending_reference,
        )
        _ensure_registration(
            db,
            mobile=KYC_PENDING_MOBILE,
            code="REG-FV2-025",
            language="te",
            full_name="QA Pending Farmer",
            status="KYC_SUBMITTED",
            user_id=pending_user.id,
            kyc_reference=pending_reference,
        )

        verified_user = _ensure_user(db, VERIFIED_MOBILE, "en", "FARMER")
        verified_reference = "KYC-QA-VERIFIED-033"
        verified_farmer = _ensure_farmer_profile(
            db,
            user=verified_user,
            code="F-FV2-033",
            name="QA Verified Farmer",
            kyc_status="KYC_VERIFIED",
            kyc_reference=verified_reference,
        )
        _ensure_registration(
            db,
            mobile=VERIFIED_MOBILE,
            code="REG-FV2-033",
            language="en",
            full_name="QA Verified Farmer",
            status="KYC_SUBMITTED",
            user_id=verified_user.id,
            kyc_reference=verified_reference,
        )

        centre, operator, scale = _ensure_qa_infrastructure(db)
        buyer = _ensure_buyer(db)
        recommendation = _ensure_market_recommendation(db)
        create_goat, _ = _ensure_verified_goat(
            db,
            verified_farmer,
            operator,
            centre,
            scale,
            code="GOAT-QA-CREATE",
            weight=Decimal("50.000"),
        )
        offer_goat, offer_weighment = _ensure_verified_goat(
            db,
            verified_farmer,
            operator,
            centre,
            scale,
            code="GOAT-QA-OFFER",
            weight=Decimal("48.500"),
        )
        _ensure_listing_with_offer(
            db,
            verified_farmer,
            offer_goat,
            offer_weighment,
            recommendation,
            buyer,
        )
        db.commit()

        print("Farmer manual-QA fixtures ready")
        print("--------------------------------")
        print(
            f"FV2-001 NEW registration : {FRESH_MOBILE} / OTP {_development_otp(FRESH_MOBILE)}"
        )
        print(
            f"FV2-017 Resume at KYC    : {IN_PROGRESS_MOBILE} / OTP {_development_otp(IN_PROGRESS_MOBILE)}"
        )
        print(
            f"FV2-025 KYC pending Home : {KYC_PENDING_MOBILE} / OTP {_development_otp(KYC_PENDING_MOBILE)}"
        )
        print(
            f"FV2-033 Verified Farmer  : {VERIFIED_MOBILE} / OTP {_development_otp(VERIFIED_MOBILE)}"
        )
        print("Verified target for Create Listing: GOAT-QA-CREATE (50.000 kg)")
        print("Published listing with active offer: PS-LST-QA-OFFER")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
