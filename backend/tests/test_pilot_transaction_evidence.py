from decimal import Decimal

from app.logistics.schemas import DeliveryRequest, PickupRequest
from app.logistics.service import calculate_tolerance
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
