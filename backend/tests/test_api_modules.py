from app.main import app


def test_module_routes_are_exposed():
    paths = app.openapi()["paths"]
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
        prefix = f"/api/v1/{module}/"
        assert any(path.startswith(prefix) for path in paths), f"No routes exposed for {module}"
