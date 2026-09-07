import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent import grafana_mcp, publish  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[1] / "samples" / "engine.output.json"


def load() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_dashboard_panels_and_severity_csv():
    dash = publish.build_dashboard(load())
    assert dash["uid"] == "backlot"
    assert [p["type"] for p in dash["panels"]] == ["stat", "bargauge", "table", "annolist"]
    csv = dash["panels"][0]["targets"][0]["csvContent"]
    assert csv.splitlines()[0] == "scene,severity"
    assert "S2,3" in csv and "S1,2" in csv
    assert dash["annotations"]["list"][0]["target"]["tags"] == ["backlot"]


def test_dashboard_deterministic():
    out = load()
    assert json.dumps(publish.build_dashboard(out), sort_keys=True) == json.dumps(publish.build_dashboard(out), sort_keys=True)


def test_annotation_count_and_tags():
    out = load()
    calls = publish.annotations_for(out, "r1", 1000)
    expected = sum(1 + len(publish.open_locks(s)) for s in out["scenes"])
    assert len(calls) == expected
    assert all(name == "create_annotation" for name, _ in calls)
    assert all("run:r1" in args["tags"] and args["time"] == 1000 for _, args in calls)
    assert calls[0][1]["tags"][:3] == ["backlot", "scene:S1", "sev:RED"]


def test_publish_mocked(monkeypatch):
    seen: list[tuple[str, dict]] = []

    async def fake_call(name: str, args: dict) -> str:
        seen.append((name, args))
        return json.dumps({"datasources": [{"uid": "backlot-testdata"}]}) if name == "list_datasources" else "{}"

    async def fake_many(calls: list[tuple[str, dict]]) -> list[str]:
        seen.extend(calls)
        return ["{}"] * len(calls)

    monkeypatch.setattr(grafana_mcp, "call", fake_call)
    monkeypatch.setattr(grafana_mcp, "call_many", fake_many)
    out = load()
    res = asyncio.run(publish.publish(out, "r2"))
    names = [n for n, _ in seen]
    assert names[:2] == ["list_datasources", "update_dashboard"]
    assert names.count("grafana_api_request") == 0
    assert res["annotations"] == sum(1 + len(publish.open_locks(s)) for s in out["scenes"])
    assert seen[1][1]["overwrite"] is True
