from decimal import Decimal
from app.marketplace.service import calculate_total_paise


def test_farmer_total_value_calculation():
    # 50 kg x Rs 400/kg = Rs 20,000 = 2,000,000 paise
    assert calculate_total_paise(Decimal("50.000"), 40000) == 2_000_000


def test_buyer_total_offer_calculation():
    # 50 kg x Rs 492/kg = Rs 24,600 = 2,460,000 paise
    assert calculate_total_paise(Decimal("50.000"), 49200) == 2_460_000
