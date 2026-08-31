from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.core.errors import AppError
from app.marketplace.schemas import ListingCreate
from app.marketplace.service import PILOT_MARKET_CODE, _validate_listing_reference, create_listing


def _listing_payload(**overrides):
    now = datetime.now(UTC)
    payload = {
        "target_type": "GOAT",
        "target_id": "PS-GOAT-TEST",
        "farmer_price_per_kg_paise": 40_000,
        "farmer_acknowledged": True,
        "sale_type": "COMPETITIVE_BIDDING",
        "opens_at": now,
        "closes_at": now + timedelta(hours=1),
    }
    payload.update(overrides)
    return payload


def test_listing_schema_requires_explicit_true_acknowledgement():
    valid = ListingCreate(**_listing_payload())
    assert valid.farmer_acknowledged is True

    missing = _listing_payload()
    missing.pop("farmer_acknowledged")
    with pytest.raises(ValidationError):
        ListingCreate(**missing)

    with pytest.raises(ValidationError):
        ListingCreate(**_listing_payload(farmer_acknowledged=False))


def test_listing_schema_types_recommendation_id_as_uuid():
    recommendation_id = uuid4()
    payload = ListingCreate(**_listing_payload(recommendation_id=str(recommendation_id)))
    assert isinstance(payload.recommendation_id, UUID)
    assert payload.recommendation_id == recommendation_id

    with pytest.raises(ValidationError):
        ListingCreate(**_listing_payload(recommendation_id="not-a-uuid"))


def test_listing_service_rejects_unacknowledged_call_before_database_work():
    now = datetime.now(UTC)
    with pytest.raises(AppError):
        create_listing(
            None,
            uuid4(),
            "GOAT",
            "PS-GOAT-TEST",
            40_000,
            False,
            "COMPETITIVE_BIDDING",
            now,
            now + timedelta(hours=1),
        )


def test_listing_reference_must_match_pilot_market():
    now = datetime.now(UTC)
    reference = SimpleNamespace(
        market_code="OTHER_MARKET",
        valid_from=now - timedelta(hours=1),
        valid_to=now + timedelta(hours=1),
    )

    with pytest.raises(AppError) as exc:
        _validate_listing_reference(reference, now)

    assert exc.value.code == "REFERENCE_MARKET_MISMATCH"


def test_listing_reference_must_be_active():
    now = datetime.now(UTC)
    expired = SimpleNamespace(
        market_code=PILOT_MARKET_CODE,
        valid_from=now - timedelta(hours=2),
        valid_to=now - timedelta(hours=1),
    )

    with pytest.raises(AppError) as exc:
        _validate_listing_reference(expired, now)

    assert exc.value.code == "REFERENCE_PRICE_NOT_ACTIVE"


def test_listing_reference_accepts_active_pilot_reference():
    now = datetime.now(UTC)
    reference = SimpleNamespace(
        market_code=PILOT_MARKET_CODE,
        valid_from=now - timedelta(hours=1),
        valid_to=now + timedelta(hours=1),
    )

    _validate_listing_reference(reference, now)
