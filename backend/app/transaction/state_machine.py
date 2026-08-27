from app.core.errors import AppError

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "OFFER_ACCEPTED": {"AGREEMENT_PENDING"},
    "AGREEMENT_PENDING": {"AGREEMENT_LOCKED"},
    "AGREEMENT_LOCKED": {"FUNDS_SECURED"},
    "FUNDS_SECURED": {"PICKUP_SCHEDULED"},
    "PICKUP_SCHEDULED": {"PICKED_UP"},
    "PICKED_UP": {"IN_TRANSIT"},
    "IN_TRANSIT": {"DELIVERED"},
    "DELIVERED": {"DELIVERY_VERIFICATION"},
    "DELIVERY_VERIFICATION": {"TOLERANCE_CHECK"},
    "TOLERANCE_CHECK": {"SETTLEMENT_READY", "DISPUTED"},
    "SETTLEMENT_READY": {"SETTLED"},
    "DISPUTED": {"RESOLVED"},
    "RESOLVED": {"SETTLED"},
    "SETTLED": {"CLOSED"},
    "CLOSED": set(),
}


def assert_transition(current: str, target: str) -> None:
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise AppError(
            "INVALID_TRANSACTION_TRANSITION",
            f"Cannot transition transaction from {current} to {target}.",
            409,
        )
