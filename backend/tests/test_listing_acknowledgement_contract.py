from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.errors import AppError
from app.marketplace.schemas import ListingCreate
from app.marketplace.service import create_listing


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
