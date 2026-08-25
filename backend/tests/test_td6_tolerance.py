from decimal import Decimal
from app.logistics.service import calculate_tolerance
def test_within_tolerance():
    d,p,a,ok=calculate_tolerance(Decimal("50"),Decimal("49.5"),150)
    assert ok is True and a==Decimal("1.5")
def test_outside_tolerance():
    d,p,a,ok=calculate_tolerance(Decimal("50"),Decimal("48"),150)
    assert ok is False
