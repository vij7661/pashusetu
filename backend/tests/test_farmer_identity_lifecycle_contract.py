import inspect

from app.identity.router import router
from app.identity.service import complete_farmer_registration_kyc, save_farmer_registration_details


def test_farmer_identity_cannot_be_created_outside_registration_kyc_flow():
    routes = {
        (route.path, method)
        for route in router.routes
        for method in getattr(route, "methods", set())
    }

    assert ("/identity/farmers", "POST") not in routes
    assert ("/identity/farmer-registration/kyc", "POST") in routes


def test_farmer_registration_details_and_kyc_identity_are_audited_atomically():
    details_source = inspect.getsource(save_farmer_registration_details)
    kyc_source = inspect.getsource(complete_farmer_registration_kyc)

    assert '"FARMER_REGISTRATION_DETAILS_SAVED"' in details_source
    assert "commit=False" in details_source
    assert '"FARMER_IDENTITY_CREATED_AT_KYC_SUBMISSION"' in kyc_source
    assert "commit=False" in kyc_source
    assert '"aadhaar_number"' not in kyc_source.split("append_event", 1)[-1]
