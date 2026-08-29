from app.main import app


def test_expected_api_modules_are_exposed():
    """Each MVP module must expose at least one real public API route.

    OpenAPI is the externally visible API contract and correctly resolves FastAPI's
    nested included routers across framework versions.
    """
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
        prefix = f"/api/v1/{module}"
        assert any(path == prefix or path.startswith(f"{prefix}/") for path in paths), (
            f"Expected API module '{module}' to expose at least one route"
        )
