from app.bidding.service import _fingerprint


def test_fingerprint_is_deterministic():
    a = _fingerprint({"listing_code": "PS-LST-1", "price_per_kg_paise": 49200})
    b = _fingerprint({"price_per_kg_paise": 49200, "listing_code": "PS-LST-1"})
    assert a == b
