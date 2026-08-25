from fastapi.testclient import TestClient
from app.main import app


def test_module_scaffolds_are_exposed():
    client = TestClient(app)
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
        response = client.get(f"/api/v1/{module}/_status")
        assert response.status_code == 200
        assert response.json()["status"] == "scaffolded"
