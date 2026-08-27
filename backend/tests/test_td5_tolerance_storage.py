import pytest
from pydantic import ValidationError

from app.agreement.schemas import AgreementCreate


def test_tolerance_percent_is_validated():
    payload = AgreementCreate(
        price_basis="DELIVERY_ADJUSTED_NET_KG",
        pickup_point="Chityal Mandal Centre",
        final_weighing_point="Buyer Verified Scale HYD-17",
        tolerance_percent=1.5,
        transport_responsibility="BUYER",
        dispute_rule="Controlled reweigh, then evidence review if unresolved.",
    )
    assert payload.tolerance_percent == 1.5


def test_unapproved_tolerance_is_rejected():
    with pytest.raises(ValidationError):
        AgreementCreate(
            price_basis="DELIVERY_ADJUSTED_NET_KG",
            pickup_point="Chityal Mandal Centre",
            final_weighing_point="Buyer Verified Scale HYD-17",
            tolerance_percent=2.0,
            transport_responsibility="BUYER",
            dispute_rule="Controlled reweigh, then evidence review if unresolved.",
        )
