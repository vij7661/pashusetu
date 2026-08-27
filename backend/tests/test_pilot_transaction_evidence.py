from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.agreement.schemas import AgreementCreate
from app.agreement.service import confirm_agreement, create_agreement
from app.logistics.schemas import DeliveryRequest, PickupRequest
from app.logistics.service import calculate_tolerance, evaluate_delivery
from app.marketplace.models import Bid, Listing
from app.transaction.state_machine import assert_transition


def test_selection_scoped_tolerance_routes_deterministically():
    inside = calculate_tolerance(Decimal(100), Decimal("98.5"), 150)
    outside = calculate_tolerance(Decimal(100), Decimal("98.499"), 150)

    assert inside[3] is True
    assert outside[3] is False
    assert_transition("TOLERANCE_CHECK", "SETTLEMENT_READY")
    assert_transition("TOLERANCE_CHECK", "DISPUTED")


def test_evidence_commands_require_retry_keys():
    pickup = PickupRequest(
        qr_verified=True,
        goat_count=2,
        loading_video_evidence_id="00000000-0000-0000-0000-000000000002",
        idempotency_key="pickup-001",
    )
    delivery = DeliveryRequest(
        qr_verified=True,
        goat_count=2,
        delivery_video_evidence_id="00000000-0000-0000-0000-000000000003",
        delivery_weighment_id="00000000-0000-0000-0000-000000000001",
        idempotency_key="delivery-001",
    )

    assert pickup.idempotency_key == "pickup-001"
    assert delivery.idempotency_key == "delivery-001"


@patch("app.agreement.service.transition_transaction")
@patch("app.agreement.service._role_for_user", return_value="FARMER")
def test_accepted_bid_creates_authoritative_commercial_snapshot(_role, transition):
    tx = SimpleNamespace(
        id=uuid4(),
        state="OFFER_ACCEPTED",
        accepted_bid_id=uuid4(),
        listing_id=uuid4(),
        farmer_profile_id=uuid4(),
        buyer_profile_id=uuid4(),
    )
    selected_goats = [uuid4(), uuid4(), uuid4()]
    bid = SimpleNamespace(
        id=tx.accepted_bid_id,
        listing_id=tx.listing_id,
        status="ACCEPTED",
        selected_weight_kg=Decimal("75.250"),
        selected_goat_ids=selected_goats,
        whole_lot=False,
        price_per_kg_paise=49_200,
    )
    listing = SimpleNamespace(id=tx.listing_id, verified_weight_kg=Decimal("120.000"))
    db = MagicMock()
    db.scalar.side_effect = [tx, 1]
    db.get.side_effect = lambda model, _id: (
        bid if model is Bid else listing if model is Listing else None
    )
    payload = AgreementCreate(
        price_basis="ORIGIN_VERIFIED_WEIGHT",
        pickup_point="Origin centre",
        final_weighing_point="Delivery centre",
        tolerance_percent=1.5,
        transport_responsibility="BUYER",
        dispute_rule="Open a controlled reweigh dispute when outside tolerance.",
    )

    snapshot = create_agreement(db, tx, uuid4(), payload)

    assert snapshot.accepted_bid_id == bid.id
    assert snapshot.selected_goat_ids == selected_goats
    assert snapshot.agreed_weight_kg == Decimal("75.250")
    assert snapshot.accepted_price_per_kg_paise == 49_200
    assert snapshot.livestock_amount_paise == 3_702_300
    assert not hasattr(snapshot, "transport_estimate_paise")
    transition.assert_called_once_with(db, tx, "AGREEMENT_PENDING")


def test_locked_agreement_confirmation_is_immutable_and_idempotent():
    db = MagicMock()
    agreement = SimpleNamespace(locked=True)

    assert confirm_agreement(db, SimpleNamespace(), agreement, uuid4(), True) is agreement
    db.commit.assert_not_called()


def test_delivery_uses_preserved_selection_weight_not_listing_aggregate():
    agreement = SimpleNamespace(agreed_weight_kg=Decimal("75.250"), tolerance_basis_points=150)
    reading = SimpleNamespace(net_kg=Decimal("74.500"))
    tx = SimpleNamespace(active_agreement_id=uuid4())
    delivery_session = SimpleNamespace(id=uuid4())
    db = MagicMock()
    db.get.return_value = agreement
    db.scalar.return_value = reading

    origin, delivery, *_rest = evaluate_delivery(db, tx, delivery_session)

    assert origin == Decimal("75.250")
    assert delivery == Decimal("74.500")
