import pytest
from pydantic import ValidationError

from app.agreement.schemas import (
    AgreementCreate,
    PILOT_DISPUTE_RULE,
    PILOT_PRICE_BASIS,
    PILOT_TRANSPORT_RESPONSIBILITY,
)


def test_farmer_agreement_payload_contains_only_transaction_specific_inputs():
    payload = AgreementCreate(
        pickup_point="Verified pickup point",
        final_weighing_point="Verified final scale",
        tolerance_percent=1.5,
    )

    assert payload.model_dump() == {
        "pickup_point": "Verified pickup point",
        "final_weighing_point": "Verified final scale",
        "tolerance_percent": 1.5,
    }


def test_client_cannot_override_server_owned_pilot_business_terms():
    with pytest.raises(ValidationError):
        AgreementCreate(
            pickup_point="Verified pickup point",
            final_weighing_point="Verified final scale",
            tolerance_percent=1.5,
            price_basis="ORIGIN_VERIFIED_WEIGHT",
            transport_responsibility="FARMER",
            dispute_rule="Client supplied rule must not become commercial truth.",
        )


def test_pilot_business_terms_are_explicit_backend_constants():
    assert PILOT_PRICE_BASIS == "DELIVERY_ADJUSTED_NET_KG"
    assert PILOT_TRANSPORT_RESPONSIBILITY == "BUYER"
    assert PILOT_DISPUTE_RULE
