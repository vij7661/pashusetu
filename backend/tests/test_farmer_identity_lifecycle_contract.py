from app.identity.router import router


def test_farmer_identity_cannot_be_created_outside_registration_kyc_flow():
    routes = {
        (route.path, method)
        for route in router.routes
        for method in getattr(route, "methods", set())
    }

    assert ("/identity/farmers", "POST") not in routes
    assert ("/identity/farmer-registration/kyc", "POST") in routes
