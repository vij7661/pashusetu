from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.audit.models import AuditEvent
from app.core.security import create_access_token
from app.db.session import get_db
from app.identity.models import User, UserRole
from app.identity.profile_models import BuyerProfile, FarmerProfile
from app.livestock.models import Goat
from app.main import app
from app.marketplace.models import Bid, Listing
from app.transaction.models import Transaction
from app.weighment.models import (
    MandalCentre,
    OperatorProfile,
    ScaleDevice,
    WeighmentSession,
    WeightReading,
)


def _headers(user: User, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(user.id), [role])}"}


def test_verified_listing_idempotent_bidding_and_single_acceptance(postgres_available):
    connection = postgres_available.connect()
    transaction = connection.begin()
    db = Session(bind=connection)
    suffix = uuid4().hex[:8]
    try:
        farmer_user = User(mobile_e164=f"+9160{suffix}")
        other_farmer_user = User(mobile_e164=f"+9150{suffix}")
        buyer_one_user = User(mobile_e164=f"+9140{suffix}")
        buyer_two_user = User(mobile_e164=f"+9130{suffix}")
        operator_user = User(mobile_e164=f"+9120{suffix}")
        db.add_all([farmer_user, other_farmer_user, buyer_one_user, buyer_two_user, operator_user])
        db.flush()
        db.add_all(
            [
                UserRole(user_id=farmer_user.id, role="FARMER"),
                UserRole(user_id=other_farmer_user.id, role="FARMER"),
                UserRole(user_id=buyer_one_user.id, role="BUYER"),
                UserRole(user_id=buyer_two_user.id, role="BUYER"),
                UserRole(user_id=operator_user.id, role="OPERATOR"),
            ]
        )
        farmer = FarmerProfile(
            user_id=farmer_user.id, farmer_code=f"F-{suffix}", full_name="Synthetic Seller"
        )
        other_farmer = FarmerProfile(
            user_id=other_farmer_user.id, farmer_code=f"OF-{suffix}", full_name="Other Seller"
        )
        buyer_one = BuyerProfile(
            user_id=buyer_one_user.id,
            buyer_code=f"B1-{suffix}",
            business_name="Synthetic Buyer One",
            buyer_type="BULK_BUYER",
        )
        buyer_two = BuyerProfile(
            user_id=buyer_two_user.id,
            buyer_code=f"B2-{suffix}",
            business_name="Synthetic Buyer Two",
            buyer_type="BULK_BUYER",
        )
        centre = MandalCentre(centre_code=f"C-{suffix}", name="Synthetic Centre")
        db.add_all([farmer, other_farmer, buyer_one, buyer_two, centre])
        db.flush()
        operator = OperatorProfile(
            user_id=operator_user.id,
            operator_code=f"OP-{suffix}",
            full_name="Synthetic Operator",
            centre_id=centre.id,
        )
        scale = ScaleDevice(
            scale_code=f"S-{suffix}", centre_id=centre.id, calibration_status="VALID", active=True
        )
        unverified_goat = Goat(
            goat_code=f"UG-{suffix}", farmer_profile_id=farmer.id, status="DRAFT"
        )
        verified_goat = Goat(goat_code=f"VG-{suffix}", farmer_profile_id=farmer.id, status="DRAFT")
        db.add_all([operator, scale, unverified_goat, verified_goat])
        db.flush()
        weighment = WeighmentSession(
            weighment_code=f"WG-{suffix}",
            target_type="GOAT",
            target_id=verified_goat.id,
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
                gross_kg=Decimal("51.500"),
                tare_kg=Decimal("1.500"),
                net_kg=Decimal("50.000"),
                stable=True,
                locked=True,
            )
        )
        db.commit()

        def override_db():
            yield db

        app.dependency_overrides[get_db] = override_db
        client = TestClient(app)
        seller_headers = _headers(farmer_user, "FARMER")
        other_seller_headers = _headers(other_farmer_user, "FARMER")
        buyer_one_headers = _headers(buyer_one_user, "BUYER")
        buyer_two_headers = _headers(buyer_two_user, "BUYER")
        window = {
            "opens_at": (datetime.now(UTC) - timedelta(minutes=1)).isoformat(),
            "closes_at": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
        }

        denied_listing = client.post(
            "/api/v1/marketplace/listings",
            json={
                "target_type": "GOAT",
                "target_id": unverified_goat.goat_code,
                "farmer_price_per_kg_paise": 40000,
                **window,
            },
            headers=seller_headers,
        )
        assert denied_listing.status_code == 409
        created = client.post(
            "/api/v1/marketplace/listings",
            json={
                "target_type": "GOAT",
                "target_id": verified_goat.goat_code,
                "farmer_price_per_kg_paise": 40000,
                **window,
            },
            headers=seller_headers,
        )
        assert created.status_code == 201
        listing_code = created.json()["listing_id"]
        assert created.json()["verified_weight_kg"] == "50.000"
        assert (
            client.get("/api/v1/marketplace/listings", headers=buyer_one_headers).json()[0][
                "listing_id"
            ]
            == listing_code
        )
        assert client.get("/api/v1/marketplace/listings", headers=other_seller_headers).json() == []

        first = client.post(
            f"/api/v1/bidding/listings/{listing_code}/bids",
            json={"price_per_kg_paise": 48000},
            headers={**buyer_one_headers, "Idempotency-Key": f"intent-1-{suffix}"},
        )
        retry = client.post(
            f"/api/v1/bidding/listings/{listing_code}/bids",
            json={"price_per_kg_paise": 48000},
            headers={**buyer_one_headers, "Idempotency-Key": f"intent-1-{suffix}"},
        )
        reused_with_change = client.post(
            f"/api/v1/bidding/listings/{listing_code}/bids",
            json={"price_per_kg_paise": 48100},
            headers={**buyer_one_headers, "Idempotency-Key": f"intent-1-{suffix}"},
        )
        new_intent = client.post(
            f"/api/v1/bidding/listings/{listing_code}/bids",
            json={"price_per_kg_paise": 48100},
            headers={**buyer_one_headers, "Idempotency-Key": f"intent-1b-{suffix}"},
        )
        second = client.post(
            f"/api/v1/bidding/listings/{listing_code}/bids",
            json={"price_per_kg_paise": 49200},
            headers={**buyer_two_headers, "Idempotency-Key": f"intent-2-{suffix}"},
        )
        assert (
            first.status_code
            == retry.status_code
            == new_intent.status_code
            == second.status_code
            == 201
        )
        assert reused_with_change.status_code == 409
        assert first.json()["bid_id"] == retry.json()["bid_id"]
        assert first.json()["total_offer_paise"] == 2_400_000
        assert second.json()["total_offer_paise"] == 2_460_000
        assert second.json()["server_sequence"] > first.json()["server_sequence"]
        listing = db.query(Listing).filter_by(listing_code=listing_code).one()
        assert db.query(Bid).filter_by(listing_id=listing.id).count() == 3
        buyer_one_bids = client.get(
            f"/api/v1/bidding/listings/{listing_code}/bids", headers=buyer_one_headers
        ).json()
        assert {row["bid_id"] for row in buyer_one_bids} == {
            first.json()["bid_id"],
            new_intent.json()["bid_id"],
        }
        assert (
            client.get(
                f"/api/v1/bidding/listings/{listing_code}/bids", headers=other_seller_headers
            ).status_code
            == 403
        )
        assert (
            client.post(
                f"/api/v1/bidding/listings/{listing_code}/bids",
                json={"price_per_kg_paise": 50000},
                headers={**seller_headers, "Idempotency-Key": f"farmer-{suffix}"},
            ).status_code
            == 409
        )
        assert (
            client.post(
                f"/api/v1/bidding/listings/{listing_code}/accept/{second.json()['bid_id']}",
                headers=other_seller_headers,
            ).status_code
            == 403
        )

        lower_denied = client.post(
            f"/api/v1/bidding/listings/{listing_code}/accept/{first.json()['bid_id']}",
            headers=seller_headers,
        )
        assert lower_denied.status_code == 409
        accepted = client.post(
            f"/api/v1/bidding/listings/{listing_code}/accept/{second.json()['bid_id']}",
            headers=seller_headers,
        )
        repeated = client.post(
            f"/api/v1/bidding/listings/{listing_code}/accept/{second.json()['bid_id']}",
            headers=seller_headers,
        )
        conflict = client.post(
            f"/api/v1/bidding/listings/{listing_code}/accept/{first.json()['bid_id']}",
            headers=seller_headers,
        )
        assert accepted.status_code == repeated.status_code == 200
        assert conflict.status_code == 409
        assert accepted.json()["accepted_bid_id"] == second.json()["bid_id"]
        assert db.query(Bid).filter_by(listing_id=listing.id, status="ACCEPTED").count() == 1
        assert db.query(Transaction).filter_by(listing_id=listing.id).count() == 1
        events = (
            db.query(AuditEvent)
            .filter_by(aggregate_type="LISTING", aggregate_id=listing.id)
            .order_by(AuditEvent.sequence)
            .all()
        )
        assert [event.event_type for event in events] == [
            "LISTING_PUBLISHED",
            "BID_SUBMITTED",
            "BID_SUBMITTED",
            "BID_SUBMITTED",
            "BID_ACCEPTED",
        ]
    finally:
        app.dependency_overrides.clear()
        db.close()
        transaction.rollback()
        connection.close()
