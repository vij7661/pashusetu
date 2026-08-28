from app.identity.schemas import BuyerProfileCreate, FarmerProfileCreate
from app.livestock.schemas import GoatCreate, LotCreate


def test_supported_farmer_language():
    payload = FarmerProfileCreate(
        full_name="Ramesh",
        preferred_language="te",
        kyc={"aadhaar_number": "999971658847", "name_as_per_aadhaar": "Kumar Agarwal", "consent": True},
        payout={"method": "UPI", "upi_id": "farmer.qa@pashusetuqa"},
    )
    assert payload.preferred_language == "te"


def test_buyer_type_validation():
    payload = BuyerProfileCreate(
        business_name="Hyderabad Meat Traders",
        buyer_type="BULK_BUYER",
        preferred_language="en",
    )
    assert payload.buyer_type == "BULK_BUYER"


def test_individual_goat_schema():
    payload = GoatCreate(breed="Sirohi", sex="MALE", age_months=14)
    assert payload.breed == "Sirohi"


def test_lot_supports_multiple_goats():
    payload = LotCreate(declared_quantity=8, goat_ids=["PS-G-1", "PS-G-2"])
    assert payload.declared_quantity == 8
    assert len(payload.goat_ids) == 2
