from fastapi.testclient import TestClient

from src.main import app


def test_app_serves_context_and_scenarios():
    client = TestClient(app)

    context = client.get("/api/context")
    scenarios = client.get("/api/scenarios")

    assert context.status_code == 200
    assert scenarios.status_code == 200
    assert context.json()["jurisdiction"]["code"] == "AB"
    assert len(scenarios.json()) >= 4


def test_analyze_works_without_adk_or_grafana_credentials():
    client = TestClient(app)

    response = client.post("/api/analyze", json={"scenario_id": "S1"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis"]["mode"] == "offline_structured_fallback"
    assert payload["analysis"]["structured_output_order"] == [
        "DiffOutput",
        "CascadeOutput",
        "HazardTagOutput",
    ]
    assert payload["safety"]["severity"] == "RED"
    assert payload["grafana"]["published"] is False
    assert "GRAFANA_URL" in payload["grafana"]["error"]
