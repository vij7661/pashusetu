import inspect
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import delete, select

from app.audit.models import AuditEvent
from app.db.session import SessionLocal
from app.marketplace.models import MarketPriceRecommendation
from app.marketplace.router import (
    admin_create_reference,
    admin_edit_reference,
    admin_references,
    admin_required,
)
from app.marketplace.schemas import AdminMarketReferenceCreate, AdminMarketReferenceEdit
from app.marketplace.service import create_market_reference, version_market_reference


def test_admin_reference_routes_use_admin_only_dependency():
    for endpoint in (admin_references, admin_create_reference, admin_edit_reference):
        dependency = inspect.signature(endpoint).parameters["user"].default.dependency
        assert dependency is admin_required


def test_reference_schema_rejects_blank_provenance_and_market():
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        AdminMarketReferenceCreate(
            market_code="  ",
            breed=None,
            price_per_kg_paise=40_000,
            source_label="local buyer quotes",
            valid_from=now,
        )
    with pytest.raises(ValidationError):
        AdminMarketReferenceCreate(
            market_code="HYDERABAD",
            breed=None,
            price_per_kg_paise=40_000,
            source_label="   ",
            valid_from=now,
        )


def test_edit_is_explicit_full_version_and_can_clear_breed():
    now = datetime.now(UTC)
    payload = AdminMarketReferenceEdit(
        market_code="hyderabad",
        breed=None,
        price_per_kg_paise=42_000,
        source_label="three verified local quotes",
        effective_from=now,
    )
    assert payload.market_code == "HYDERABAD"
    assert payload.breed is None
    assert payload.price_per_kg_paise == 42_000


def test_reference_edit_versions_instead_of_overwriting_history():
    db = SessionLocal()
    original_id = None
    replacement_id = None
    try:
        start = datetime.now(UTC) - timedelta(hours=2)
        effective = datetime.now(UTC) - timedelta(hours=1)
        market = f"TEST-{uuid4().hex[:8].upper()}"

        original = create_market_reference(
            db,
            market,
            "Sirohi",
            40_000,
            "pilot evidence A",
            start,
            None,
        )
        original_id = original.id

        replacement = version_market_reference(
            db,
            original.id,
            effective,
            None,
            market,
            None,
            42_000,
            "pilot evidence B",
        )
        replacement_id = replacement.id

        historical = db.get(MarketPriceRecommendation, original.id)
        current = db.get(MarketPriceRecommendation, replacement.id)
        assert historical is not None
        assert current is not None
        assert historical.id != current.id
        assert historical.price_per_kg_paise == 40_000
        assert historical.breed == "Sirohi"
        assert historical.valid_to == effective
        assert current.price_per_kg_paise == 42_000
        assert current.breed is None
        assert current.source_label == "pilot evidence B"

        old_events = list(
            db.scalars(
                select(AuditEvent).where(
                    AuditEvent.aggregate_type == "MARKET_REFERENCE",
                    AuditEvent.aggregate_id == historical.id,
                )
            ).all()
        )
        new_events = list(
            db.scalars(
                select(AuditEvent).where(
                    AuditEvent.aggregate_type == "MARKET_REFERENCE",
                    AuditEvent.aggregate_id == current.id,
                )
            ).all()
        )
        assert {event.event_type for event in old_events} == {
            "MARKET_REFERENCE_CREATED",
            "MARKET_REFERENCE_SUPERSEDED",
        }
        assert {event.event_type for event in new_events} == {"MARKET_REFERENCE_VERSION_CREATED"}
    finally:
        ids = [value for value in (original_id, replacement_id) if value is not None]
        if ids:
            db.execute(delete(AuditEvent).where(AuditEvent.aggregate_id.in_(ids)))
            db.execute(delete(MarketPriceRecommendation).where(MarketPriceRecommendation.id.in_(ids)))
            db.commit()
        db.close()
