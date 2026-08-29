from app.main import app


def test_expected_api_modules_are_exposed():
    """Each MVP module must expose at least one real API route.

    The old test required temporary /_status scaffold endpoints even after the
    modules gained real routes. That no longer represented the product contract.
    """
    paths = {
        path
        for route in app.routes
        if (path := getattr(route, "path", "")).startswith("/api/v1/")
    }
    for module in [
        "livestock",
        "weighment",
        "marketplace",
        "bidding",
        "agreement",
        "transaction",
        "logistics",
        "payments",
        "disputes",
        "notifications",
        "audit",
    ]:
        prefix = f"/api/v1/{module}"
        assert any(path == prefix or path.startswith(f"{prefix}/") for path in paths), (
            f"Expected API module '{module}' to expose at least one route"
        )
