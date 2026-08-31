from app.main import app


def test_expected_api_modules_are_exposed():
    """Each MVP module must expose at least one real public API route."""
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


def test_farmer_manual_qa_read_contracts_are_exposed():
    paths = app.openapi()["paths"]
    assert "/api/v1/marketplace/listings/eligibility" in paths
    assert "get" in paths["/api/v1/marketplace/listings/eligibility"]
    assert "/api/v1/marketplace/farmers/me/listings" in paths
    assert "get" in paths["/api/v1/marketplace/farmers/me/listings"]
    assert "/api/v1/transaction/mine" in paths
    assert "get" in paths["/api/v1/transaction/mine"]
