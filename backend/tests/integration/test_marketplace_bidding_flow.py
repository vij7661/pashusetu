from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.agreement.models import Agreement
from app.audit.models import AuditEvent
from app.core.security import create_access_token
from app.db.session import get_db
from app.disputes.models import Dispute
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
            client.get(
                "/api/v1/marketplace/listings?required_quantity=3",
                headers=buyer_one_headers,
            ).json()
            == []
        )
        assert (
            client.get(
                "/api/v1/marketplace/listings?required_quantity=1",
                headers=buyer_one_headers,
            ).status_code
            == 400
        )
        assert (
            client.get(
                "/api/v1/marketplace/listings?required_quantity=2",
                headers=buyer_one_headers,
            ).status_code
            == 400
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
        assert accepted.json()["transaction_id"].startswith("TX-")
        accepted_buyer_bid = client.get(
            f"/api/v1/bidding/listings/{listing_code}/bids", headers=buyer_two_headers
        ).json()[0]
        assert accepted_buyer_bid["transaction_id"] == accepted.json()["transaction_id"]
        assert db.query(Bid).filter_by(listing_id=listing.id, status="ACCEPTED").count() == 1
        assert db.query(Transaction).filter_by(listing_id=listing.id).count() == 1
        transaction_code = accepted.json()["transaction_id"]
        agreement = client.post(
            f"/api/v1/agreement/transactions/{transaction_code}",
            headers=seller_headers,
            json={
                "price_basis": "ORIGIN_VERIFIED_WEIGHT",
                "pickup_point": "Synthetic origin centre",
                "final_weighing_point": "Synthetic delivery centre",
                "tolerance_percent": 1.5,
                "transport_responsibility": "BUYER",
                "dispute_rule": "Controlled reweigh and evidence review when outside tolerance.",
            },
        )
        assert agreement.status_code == 201
        assert agreement.json()["accepted_price_per_kg_paise"] == 49_200
        assert agreement.json()["agreed_weight_kg"] == 50.0
        assert agreement.json()["livestock_amount_paise"] == 2_460_000
        agreement_code = agreement.json()["agreement_id"]
        for headers in (seller_headers, buyer_two_headers):
            confirmed = client.post(
                f"/api/v1/agreement/transactions/{transaction_code}/{agreement_code}/confirm",
                headers=headers,
                json={"confirm": True},
            )
            assert confirmed.status_code == 200
        assert confirmed.json()["locked"] is True
        assert (
            db.query(Agreement)
            .filter_by(
                transaction_id=db.query(Transaction)
                .filter_by(transaction_code=transaction_code)
                .one()
                .id
            )
            .count()
            == 1
        )

        secured = client.post(
            f"/api/v1/payments/transactions/{transaction_code}/secure",
            headers=buyer_two_headers,
        )
        assert secured.status_code == 200 and secured.json()["transaction_state"] == "FUNDS_SECURED"
        assigned = client.post(
            f"/api/v1/logistics/transactions/{transaction_code}/transport",
            headers=buyer_two_headers,
            json={
                "transporter_name": "Synthetic Transport",
                "driver_name": "Synthetic Driver",
                "driver_phone": "+910000000000",
                "vehicle_number": "TEST-001",
            },
        )
        assert assigned.status_code == 200
        pickup_payload = {
            "qr_verified": True,
            "goat_count": 1,
            "loading_video_evidence_id": str(uuid4()),
            "departure_note": "Synthetic pickup",
            "idempotency_key": f"pickup-{suffix}",
        }
        picked_up = client.post(
            f"/api/v1/logistics/transactions/{transaction_code}/pickup",
            headers=_headers(operator_user, "OPERATOR"),
            json=pickup_payload,
        )
        pickup_retry = client.post(
            f"/api/v1/logistics/transactions/{transaction_code}/pickup",
            headers=_headers(operator_user, "OPERATOR"),
            json=pickup_payload,
        )
        assert picked_up.status_code == pickup_retry.status_code == 200
        assert picked_up.json()["pickup_id"] == pickup_retry.json()["pickup_id"]

        delivery_weighment = WeighmentSession(
            weighment_code=f"DW-{suffix}",
            target_type="GOAT",
            target_id=verified_goat.id,
            farmer_profile_id=farmer.id,
            operator_id=operator.id,
            centre_id=centre.id,
            scale_id=scale.id,
            status="VERIFIED",
        )
        db.add(delivery_weighment)
        db.flush()
        db.add(
            WeightReading(
                weighment_session_id=delivery_weighment.id,
                sequence_no=1,
                gross_kg=Decimal("51.000"),
                tare_kg=Decimal("1.500"),
                net_kg=Decimal("49.500"),
                stable=True,
                locked=True,
            )
        )
        db.commit()
        delivery_payload = {
            "qr_verified": True,
            "goat_count": 1,
            "delivery_video_evidence_id": str(uuid4()),
            "delivery_weighment_id": delivery_weighment.weighment_code,
            "idempotency_key": f"delivery-{suffix}",
        }
        delivered = client.post(
            f"/api/v1/logistics/transactions/{transaction_code}/delivery",
            headers=_headers(operator_user, "OPERATOR"),
            json=delivery_payload,
        )
        delivery_retry = client.post(
            f"/api/v1/logistics/transactions/{transaction_code}/delivery",
            headers=_headers(operator_user, "OPERATOR"),
            json=delivery_payload,
        )
        assert delivered.status_code == delivery_retry.status_code == 200
        assert delivered.json()["within_tolerance"] is True
        assert delivered.json()["route"] == "SETTLEMENT"
        assert (
            client.get(f"/api/v1/transaction/{transaction_code}", headers=seller_headers).json()[
                "state"
            ]
            == "SETTLEMENT_READY"
        )
        outside_goat = Goat(
            goat_code=f"OG-{suffix}", farmer_profile_id=farmer.id, status="VERIFIED"
        )
        db.add(outside_goat)
        db.flush()
        outside_origin = WeighmentSession(
            weighment_code=f"OW-{suffix}",
            target_type="GOAT",
            target_id=outside_goat.id,
            farmer_profile_id=farmer.id,
            operator_id=operator.id,
            centre_id=centre.id,
            scale_id=scale.id,
            status="VERIFIED",
        )
        db.add(outside_origin)
        db.flush()
        db.add(
            WeightReading(
                weighment_session_id=outside_origin.id,
                sequence_no=1,
                gross_kg=Decimal("51.500"),
                tare_kg=Decimal("1.500"),
                net_kg=Decimal("50.000"),
                stable=True,
                locked=True,
            )
        )
        outside_listing = Listing(
            listing_code=f"OL-{suffix}",
            seller_farmer_profile_id=farmer.id,
            target_type="GOAT",
            target_id=outside_goat.id,
            weighment_session_id=outside_origin.id,
            verified_weight_kg=Decimal("50.000"),
            pricing_mode="PER_KG",
            farmer_price_per_kg_paise=40_000,
            farmer_total_value_paise=2_000_000,
            sale_type="COMPETITIVE_BIDDING",
            opens_at=datetime.now(UTC) - timedelta(minutes=1),
            closes_at=datetime.now(UTC) + timedelta(hours=1),
            status="OFFER_ACCEPTED",
        )
        db.add(outside_listing)
        db.flush()
        outside_bid = Bid(
            bid_code=f"OB-{suffix}",
            listing_id=outside_listing.id,
            buyer_profile_id=buyer_one.id,
            price_per_kg_paise=48_000,
            total_offer_paise=2_400_000,
            idempotency_key=f"outside-{suffix}",
            server_sequence=1,
            status="ACCEPTED",
            selected_goat_ids=[],
            selected_quantity=1,
            selected_weight_kg=Decimal("50.000"),
            whole_lot=True,
        )
        db.add(outside_bid)
        db.flush()
        outside_listing.accepted_bid_id = outside_bid.id
        outside_tx = Transaction(
            transaction_code=f"OTX-{suffix}",
            listing_id=outside_listing.id,
            farmer_profile_id=farmer.id,
            buyer_profile_id=buyer_one.id,
            accepted_bid_id=outside_bid.id,
            state="IN_TRANSIT",
        )
        db.add(outside_tx)
        db.flush()
        outside_agreement = Agreement(
            agreement_code=f"OAGR-{suffix}",
            transaction_id=outside_tx.id,
            version=1,
            accepted_bid_id=outside_bid.id,
            listing_id=outside_listing.id,
            farmer_profile_id=farmer.id,
            buyer_profile_id=buyer_one.id,
            selected_goat_ids=[],
            whole_lot=True,
            accepted_price_per_kg_paise=48_000,
            agreed_weight_kg=Decimal("50.000"),
            livestock_amount_paise=2_400_000,
            price_basis="ORIGIN_VERIFIED_WEIGHT",
            pickup_point="Synthetic origin centre",
            final_weighing_point="Synthetic delivery centre",
            tolerance_basis_points=150,
            transport_responsibility="BUYER",
            dispute_rule="Controlled reweigh and evidence review when outside tolerance.",
            status="LOCKED",
            locked=True,
        )
        db.add(outside_agreement)
        db.flush()
        outside_tx.active_agreement_id = outside_agreement.id
        outside_final = WeighmentSession(
            weighment_code=f"ODW-{suffix}",
            target_type="GOAT",
            target_id=outside_goat.id,
            farmer_profile_id=farmer.id,
            operator_id=operator.id,
            centre_id=centre.id,
            scale_id=scale.id,
            status="VERIFIED",
        )
        db.add(outside_final)
        db.flush()
        db.add(
            WeightReading(
                weighment_session_id=outside_final.id,
                sequence_no=1,
                gross_kg=Decimal("49.500"),
                tare_kg=Decimal("1.500"),
                net_kg=Decimal("48.000"),
                stable=True,
                locked=True,
            )
        )
        db.commit()
        outside_payload = {
            "qr_verified": True,
            "goat_count": 1,
            "delivery_video_evidence_id": str(uuid4()),
            "delivery_weighment_id": outside_final.weighment_code,
            "idempotency_key": f"outside-delivery-{suffix}",
        }
        outside = client.post(
            f"/api/v1/logistics/transactions/{outside_tx.transaction_code}/delivery",
            headers=_headers(operator_user, "OPERATOR"),
            json=outside_payload,
        )
        outside_retry = client.post(
            f"/api/v1/logistics/transactions/{outside_tx.transaction_code}/delivery",
            headers=_headers(operator_user, "OPERATOR"),
            json=outside_payload,
        )
        assert outside.status_code == outside_retry.status_code == 200
        assert outside.json()["within_tolerance"] is False
        assert outside.json()["route"] == "DISPUTE"
        assert outside_tx.state == "DISPUTED"
        assert db.query(Dispute).filter_by(transaction_id=outside_tx.id).count() == 1

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
