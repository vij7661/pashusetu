from decimal import Decimal
import pytest
from pydantic import ValidationError

from app.weighment.schemas import ReadingCreate
from app.weighment.scale_adapter import SimulatedScaleAdapter


def test_net_weight_math():
    payload = ReadingCreate(gross_kg=Decimal("54.500"), tare_kg=Decimal("4.500"), stable=True)
    assert payload.gross_kg - payload.tare_kg == Decimal("50.000")


def test_tare_must_be_less_than_gross():
    with pytest.raises(ValidationError):
        ReadingCreate(gross_kg=Decimal("10.000"), tare_kg=Decimal("10.000"), stable=True)


def test_simulated_scale_adapter():
    adapter = SimulatedScaleAdapter(Decimal("54.500"), Decimal("4.500"), stable=True)
    adapter.connect()
    sample = adapter.read_sample()
    assert sample.net_kg == Decimal("50.000")
    assert sample.stable is True
    adapter.disconnect()
