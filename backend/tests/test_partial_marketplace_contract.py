from decimal import Decimal

from app.marketplace.service import calculate_total_paise


def test_selected_verified_weights_are_summed_without_equal_division():
    selected_weights = [Decimal("10.250"), Decimal("11.500"), Decimal("12.750")]
    selected_total = sum(selected_weights, Decimal(0))
    assert selected_total == Decimal("34.500")
    assert calculate_total_paise(selected_total, 49200) == 1_697_400


def test_transport_estimate_is_separate_from_commercial_offer():
    commercial_offer = calculate_total_paise(Decimal("34.500"), 49200)
    base_paise = 50_000
    per_km_paise = 1_500
    distance_km = 12
    transport = base_paise + per_km_paise * distance_km
    assert transport == 68_000
    assert commercial_offer == 1_697_400
    assert commercial_offer + transport == 1_765_400
