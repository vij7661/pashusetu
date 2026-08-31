import pytest
from pydantic import ValidationError

from app.livestock.schemas import GoatResponse, LotResponse


def test_goat_response_rejects_invalid_sex_or_age():
    GoatResponse(
        goat_id="PS-G-1",
        breed=None,
        sex="MALE",
        age_months=18,
        health_notes=None,
        status="DRAFT",
    )

    with pytest.raises(ValidationError):
        GoatResponse(
            goat_id="PS-G-1",
            breed=None,
            sex="INVALID",
            age_months=18,
            health_notes=None,
            status="DRAFT",
        )

    with pytest.raises(ValidationError):
        GoatResponse(
            goat_id="PS-G-1",
            breed=None,
            sex="MALE",
            age_months=301,
            health_notes=None,
            status="DRAFT",
        )


def test_lot_response_rejects_impossible_linked_quantity():
    LotResponse(
        lot_id="PS-L-1",
        declared_quantity=2,
        linked_goat_ids=["PS-G-1"],
        breed_summary=None,
        sex_summary=None,
        age_summary=None,
        status="DRAFT",
    )

    with pytest.raises(ValidationError):
        LotResponse(
            lot_id="PS-L-1",
            declared_quantity=1,
            linked_goat_ids=["PS-G-1", "PS-G-2"],
            breed_summary=None,
            sex_summary=None,
            age_summary=None,
            status="DRAFT",
        )
