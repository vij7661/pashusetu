from app.main import app


def test_required_api_modules_are_exposed():
    paths = set(app.openapi()["paths"])

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
        assert any(path.startswith(prefix) for path in paths), (
            f"Expected at least one API route for module {module!r}"
        )
