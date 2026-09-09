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


def test_health_exposes_runtime_contract_without_secrets():
    payload = TestClient(app).get("/api/health").json()

    assert payload["status"] == "ok"
    assert payload["analysis"]["provider"] == "google_adk_gemini"
    assert payload["analysis"]["fallback_available"] is True
    assert payload["safety"] == {"engine": "deterministic_python", "configured": True}
    assert payload["frontend"]["same_origin_api"] is True


def test_analyze_works_without_adk_or_grafana_credentials(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GRAFANA_MCP_URL", raising=False)
    monkeypatch.delenv("GRAFANA_URL", raising=False)
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
    assert payload["runtime"]["delivery"] == "live_request"
    assert payload["safety"]["severity"] == "RED"
    assert payload["grafana"]["published"] is False
    assert "GRAFANA_URL" in payload["grafana"]["error"]


def test_custom_revision_uses_supplied_json_fields():
    response = TestClient(app).post(
        "/api/analyze",
        json={
            "scenario_id": "CUSTOM",
            "scene_id": "CUSTOM-1",
            "scene_heading": "INT. TEST STAGE - DAY",
            "original_text": "A quiet room.",
            "revised_text": "A quiet room. A practical flash pot explodes.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["scene"]["id"] == "CUSTOM-1"
    assert payload["scene"]["heading"] == "INT. TEST STAGE - DAY"
    assert payload["scene"]["revised_script"].endswith("flash pot explodes.")
    assert payload["safety"]["severity"] == "RED"


def test_script_payload_is_bounded():
    response = TestClient(app).post(
        "/api/analyze",
        json={
            "scenario_id": "CUSTOM",
            "original_text": "x" * 25_001,
            "revised_text": "A valid revision.",
        },
    )

    assert response.status_code == 422
