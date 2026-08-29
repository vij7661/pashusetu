from app.core.enums import TransactionState


def test_shared_state_machine_contains_approved_states():
    states = {x.value for x in TransactionState}
    required = {
        "DRAFT",
        "AWAITING_VERIFICATION",
        "VERIFIED",
        "PUBLISHED",
        "BIDDING",
        "OFFER_ACCEPTED",
        "AGREEMENT_PENDING",
        "AGREEMENT_LOCKED",
        "FUNDS_SECURED",
        "PICKUP_SCHEDULED",
        "PICKED_UP",
        "IN_TRANSIT",
        "DELIVERED",
        "DELIVERY_VERIFICATION",
        "TOLERANCE_CHECK",
        "SETTLEMENT_READY",
        "SETTLED",
        "DISPUTED",
        "RESOLVED",
        "CLOSED",
    }
    assert required == states
