import argparse
from datetime import datetime, timezone
from decimal import Decimal
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import select, text
from sqlalchemy.engine import make_url

import app.db.models  # noqa: F401
from app.core.config import get_settings
from app.db.base import Base
from app.db.qa_fixtures import (
    QA_CENTRE_CODE,
    QA_LISTING_CODE,
    QA_SCALE_CODE,
    QA_SUB3_GOAT_CODES,
    QA_SUB3_LOT_CODE,
    QA_UNVERIFIED_GOAT_CODE,
    QA_USERS,
    QA_VERIFIED_GOAT_CODES,
    QA_VERIFIED_LOT_CODE,
)
from app.db.session import SessionLocal
from app.identity.models import User, UserRole
from app.identity.profile_models import BuyerProfile, FarmerProfile
from app.livestock.models import Goat, Lot, LotGoat
from app.marketplace.models import Listing, MarketPriceRecommendation
from app.weighment.models import (
    FarmerWeighmentAcknowledgement,
    MandalCentre,
    OperatorProfile,
    ScaleDevice,
    WeighmentSession,
    WeightReading,
)

QA_DATABASE_NAME = "pashusetu_qa"


def fixture_uuid(key: str):
    return uuid5(NAMESPACE_URL, f"pashusetu-qa:{key}")


def assert_safe_qa_database(db) -> None:
    settings = get_settings()
    configured_database = make_url(settings.database_url).database
    actual_database = db.scalar(text("SELECT current_database()"))
    if (
        settings.app_env.lower() != "qa"
        or not settings.database_isolated_for_qa
        or not settings.otp_test_mode
        or configured_database != QA_DATABASE_NAME
        or actual_database != QA_DATABASE_NAME
    ):
        raise RuntimeError(
            "Refusing QA mutation: requires APP_ENV=qa, enabled QA isolation/test OTP, "
            f"and configured/actual database {QA_DATABASE_NAME!r}"
        )


def reset_qa_database(db) -> None:
    assert_safe_qa_database(db)
    table_names = [f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables)]
    if table_names:
        db.execute(text(f"TRUNCATE TABLE {', '.join(table_names)} RESTART IDENTITY CASCADE"))
    db.commit()


def seed_qa_database(db) -> None:
    assert_safe_qa_database(db)
    users = {}
    for fixture in QA_USERS:
        user = User(
            id=fixture_uuid(fixture.fixture_id),
            mobile_e164=fixture.mobile_e164,
            preferred_language=fixture.language,
            status="ACTIVE",
        )
        db.add(user)
        db.flush()
        db.add(
            UserRole(
                id=fixture_uuid(f"{fixture.fixture_id}:role"),
                user_id=user.id,
                role=fixture.role,
            )
        )
        users[fixture.fixture_id] = user

    farmers = {}
    for fixture_id, verified in (
        ("FARMER_EN_001", True),
        ("FARMER_SUB3_001", True),
    ):
        profile = FarmerProfile(
            id=fixture_uuid(f"{fixture_id}:profile"),
            user_id=users[fixture_id].id,
            farmer_code=fixture_id,
            full_name=f"Synthetic {fixture_id}",
            village="QA Village",
            mandal="QA Mandal",
            district="QA District",
            state="Telangana",
            kyc_status="VERIFIED" if verified else "PENDING",
            kyc_masked_id="XXXXXXXX7058" if fixture_id == "FARMER_EN_001" else "XXXXXXXX9405",
            kyc_provider_reference=f"QA-KYC-KYC_{fixture_id}",
            payout_status="VERIFIED" if verified else "PENDING",
            payout_method="UPI",
            payout_masked_reference="f***@pashusetuqa",
        )
        db.add(profile)
        farmers[fixture_id] = profile

    buyer = BuyerProfile(
        id=fixture_uuid("BUYER_001:profile"),
        user_id=users["BUYER_001"].id,
        buyer_code="BUYER_001",
        business_name="Synthetic QA Buyer",
        contact_person="Synthetic Buyer Contact",
        buyer_type="BULK_BUYER",
        city="QA City",
        state="Telangana",
        kyc_status="VERIFIED",
        business_verified=True,
    )
    centre = MandalCentre(
        id=fixture_uuid(QA_CENTRE_CODE),
        centre_code=QA_CENTRE_CODE,
        name="Synthetic QA Mandal Centre",
        village="QA Village",
        mandal="QA Mandal",
        district="QA District",
        state="Telangana",
        latitude=Decimal("17.000000"),
        longitude=Decimal("79.000000"),
    )
    db.add_all([buyer, centre])
    db.flush()
    operator = OperatorProfile(
        id=fixture_uuid("OPERATOR_001:profile"),
        user_id=users["OPERATOR_001"].id,
        operator_code="OPERATOR_001",
        full_name="Synthetic QA Operator",
        centre_id=centre.id,
    )
    scale = ScaleDevice(
        id=fixture_uuid(QA_SCALE_CODE),
        scale_code=QA_SCALE_CODE,
        centre_id=centre.id,
        vendor="SYNTHETIC",
        model="QA-SCALE",
        bluetooth_identifier="QA-NO-DEVICE",
        calibration_status="VALID",
    )
    db.add_all([operator, scale])
    db.flush()

    verified_goats = []
    for index, code in enumerate(QA_VERIFIED_GOAT_CODES, start=1):
        goat = Goat(
            id=fixture_uuid(code),
            goat_code=code,
            farmer_profile_id=farmers["FARMER_EN_001"].id,
            breed="Synthetic Osmanabadi",
            sex="MALE" if index % 2 else "FEMALE",
            age_months=12 + index,
            health_notes="Synthetic QA fixture",
            status="VERIFIED",
        )
        db.add(goat)
        verified_goats.append(goat)
    db.add(
        Goat(
            id=fixture_uuid(QA_UNVERIFIED_GOAT_CODE),
            goat_code=QA_UNVERIFIED_GOAT_CODE,
            farmer_profile_id=farmers["FARMER_EN_001"].id,
            breed="Synthetic Local",
            sex="FEMALE",
            age_months=10,
            health_notes="Synthetic unverified fixture",
            status="DRAFT",
        )
    )
    sub3_goats = []
    for code in QA_SUB3_GOAT_CODES:
        goat = Goat(
            id=fixture_uuid(code),
            goat_code=code,
            farmer_profile_id=farmers["FARMER_SUB3_001"].id,
            breed="Synthetic Local",
            sex="MALE",
            age_months=11,
            health_notes="Synthetic fewer-than-three fixture",
            status="VERIFIED",
        )
        db.add(goat)
        sub3_goats.append(goat)
    db.flush()

    verified_lot = Lot(
        id=fixture_uuid(QA_VERIFIED_LOT_CODE),
        lot_code=QA_VERIFIED_LOT_CODE,
        farmer_profile_id=farmers["FARMER_EN_001"].id,
        declared_quantity=3,
        breed_summary="Synthetic Osmanabadi",
        sex_summary="Mixed",
        age_summary="12-15 months",
        health_notes="Synthetic verified QA lot",
        status="VERIFIED",
    )
    sub3_lot = Lot(
        id=fixture_uuid(QA_SUB3_LOT_CODE),
        lot_code=QA_SUB3_LOT_CODE,
        farmer_profile_id=farmers["FARMER_SUB3_001"].id,
        declared_quantity=2,
        breed_summary="Synthetic Local",
        sex_summary="Male",
        age_summary="11 months",
        health_notes="Synthetic fewer-than-three QA lot",
        status="DRAFT",
    )
    db.add_all([verified_lot, sub3_lot])
    db.flush()
    for goat in verified_goats:
        db.add(LotGoat(id=fixture_uuid(f"{QA_VERIFIED_LOT_CODE}:{goat.goat_code}"), lot_id=verified_lot.id, goat_id=goat.id))
    for goat in sub3_goats:
        db.add(LotGoat(id=fixture_uuid(f"{QA_SUB3_LOT_CODE}:{goat.goat_code}"), lot_id=sub3_lot.id, goat_id=goat.id))

    weighment = WeighmentSession(
        id=fixture_uuid("QA-WEIGHMENT-001"),
        weighment_code="QA-WEIGHMENT-001",
        target_type="LOT",
        target_id=verified_lot.id,
        farmer_profile_id=farmers["FARMER_EN_001"].id,
        operator_id=operator.id,
        centre_id=centre.id,
        scale_id=scale.id,
        status="ACKNOWLEDGED",
    )
    recommendation = MarketPriceRecommendation(
        id=fixture_uuid("QA-MARKET-PRICE-001"),
        market_code="QA-MARKET",
        breed="Synthetic Osmanabadi",
        price_per_kg_paise=45000,
        source_label="Synthetic QA fixture",
        valid_from=datetime(2020, 1, 1, tzinfo=timezone.utc),
        valid_to=datetime(2035, 1, 1, tzinfo=timezone.utc),
    )
    db.add_all([weighment, recommendation])
    db.flush()
    db.add_all(
        [
            WeightReading(
                id=fixture_uuid("QA-WEIGHT-READING-001"),
                weighment_session_id=weighment.id,
                sequence_no=1,
                gross_kg=Decimal("94.000"),
                tare_kg=Decimal("4.000"),
                net_kg=Decimal("90.000"),
                stable=True,
                locked=True,
            ),
            FarmerWeighmentAcknowledgement(
                id=fixture_uuid("QA-WEIGHMENT-ACK-001"),
                weighment_session_id=weighment.id,
                farmer_profile_id=farmers["FARMER_EN_001"].id,
                acknowledged=True,
            ),
            Listing(
                id=fixture_uuid(QA_LISTING_CODE),
                listing_code=QA_LISTING_CODE,
                seller_farmer_profile_id=farmers["FARMER_EN_001"].id,
                target_type="LOT",
                target_id=verified_lot.id,
                weighment_session_id=weighment.id,
                verified_weight_kg=Decimal("90.000"),
                farmer_price_per_kg_paise=46000,
                farmer_total_value_paise=4140000,
                recommendation_id=recommendation.id,
                sale_type="COMPETITIVE_BIDDING",
                opens_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
                closes_at=datetime(2035, 1, 1, tzinfo=timezone.utc),
                status="LIVE",
            ),
        ]
    )
    db.commit()


def fixture_counts(db) -> dict[str, int]:
    return {
        "users": len(db.scalars(select(User)).all()),
        "farmers": len(db.scalars(select(FarmerProfile)).all()),
        "buyers": len(db.scalars(select(BuyerProfile)).all()),
        "goats": len(db.scalars(select(Goat)).all()),
        "lots": len(db.scalars(select(Lot)).all()),
        "listings": len(db.scalars(select(Listing)).all()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Guarded PashuSetu isolated QA fixture tool")
    parser.add_argument("command", choices=("reset-seed",))
    args = parser.parse_args()
    with SessionLocal() as db:
        if args.command == "reset-seed":
            reset_qa_database(db)
        seed_qa_database(db)
        print(f"QA fixtures ready: {fixture_counts(db)}")


if __name__ == "__main__":
    main()
