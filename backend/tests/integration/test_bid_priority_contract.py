from app.bidding.service import _fingerprint

def test_retry_fingerprint_contract():
    a = _fingerprint({"listing_code":"PS-LST-DEMO","price_per_kg_paise":49200})
    b = _fingerprint({"price_per_kg_paise":49200,"listing_code":"PS-LST-DEMO"})
    assert a == b
