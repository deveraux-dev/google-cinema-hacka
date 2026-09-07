"""Publish engine.run() output to Grafana via MCP: testdata-backed wall + one annotation per scene/open lock."""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time

from agent import grafana_mcp
from agent.harness import DEFAULT_SAMPLES, _run

DS_UID = "backlot-testdata"
DS_TYPE = "grafana-testdata-datasource"
DASH_UID = "backlot"
SEVERITY = {"GREEN": 0, "AMBER": 1, "RED": 2, "STOP": 3}
COLORS = {"GREEN": "green", "AMBER": "orange", "RED": "red", "STOP": "dark-red"}


def _csv(rows: list[list[str]]) -> str:
    def cell(v: object) -> str:
        s = str(v).replace('"', "'")
        return f'"{s}"' if any(c in s for c in ",\n") else s

    return "\n".join(",".join(cell(v) for v in row) for row in rows)


def _panel(pid: int, ptype: str, title: str, grid: dict, csv: str, **extra: object) -> dict:
    return {
        "id": pid,
        "type": ptype,
        "title": title,
        "gridPos": grid,
        "datasource": {"type": DS_TYPE, "uid": DS_UID},
        "targets": [{"refId": "A", "scenarioId": "csv_content", "csvContent": csv, "datasource": {"type": DS_TYPE, "uid": DS_UID}}],
        **extra,
    }


def open_locks(scene: dict) -> list[dict]:
    return [lk for lk in scene["locks"] if lk["released"] is None]


def build_dashboard(out: dict) -> dict:
    scenes = out["scenes"]
    sev_csv = _csv([["scene", "severity"], *[[s["id"], SEVERITY[s["severity"]]] for s in scenes]])
    open_csv = _csv([["scene", "open"], *[[s["id"], len(open_locks(s))] for s in scenes]])
    fa_rows = [["scene", "table", "band", "headcount_row", "requirement"]]
    for s in scenes:
        fa = s["first_aid"]
        fa_rows.append([s["id"], fa.get("table", ""), fa.get("band", ""), fa.get("headcount_row", ""), fa.get("requirement", "")])
    mappings = [{"type": "value", "options": {str(v): {"text": k, "color": COLORS[k], "index": v}}} for k, v in SEVERITY.items()]
    panels = [
        _panel(
            1, "stat", "Severity per scene", {"x": 0, "y": 0, "w": 12, "h": 6}, sev_csv,
            options={"colorMode": "background", "graphMode": "none", "textMode": "value_and_name", "reduceOptions": {"calcs": ["lastNotNull"], "fields": "/^severity$/"}},
            fieldConfig={"defaults": {"mappings": mappings, "color": {"mode": "thresholds"}, "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}, {"color": "orange", "value": 1}, {"color": "red", "value": 2}, {"color": "dark-red", "value": 3}]}}, "overrides": []},
            transformations=[{"id": "rowsToFields", "options": {}}],
        ),
        _panel(
            2, "bargauge", "Open locks per scene", {"x": 12, "y": 0, "w": 12, "h": 6}, open_csv,
            options={"orientation": "horizontal", "displayMode": "gradient", "reduceOptions": {"calcs": ["lastNotNull"], "fields": "/^open$/"}},
            fieldConfig={"defaults": {"color": {"mode": "continuous-GrYlRd"}, "min": 0}, "overrides": []},
            transformations=[{"id": "rowsToFields", "options": {}}],
        ),
        _panel(3, "table", "First aid (Schedule 2)", {"x": 0, "y": 6, "w": 12, "h": 8}, _csv(fa_rows), options={"cellHeight": "sm"}),
        {
            "id": 4, "type": "annolist", "title": "Lock events", "gridPos": {"x": 12, "y": 6, "w": 12, "h": 8},
            "options": {"onlyFromThisDashboard": False, "onlyInTimeRange": False, "tags": ["backlot"], "limit": 50, "showUser": False, "showTime": True, "showTags": True},
        },
    ]
    return {
        "uid": DASH_UID,
        "title": "Backlot Safety Wall",
        "tags": ["backlot"],
        "timezone": "browser",
        "schemaVersion": 39,
        "refresh": "10s",
        "time": {"from": "now-6h", "to": "now"},
        "annotations": {"list": [{"name": "Backlot", "enable": True, "iconColor": "red", "datasource": {"type": "grafana", "uid": "-- Grafana --"}, "target": {"type": "tags", "tags": ["backlot"], "matchAny": False, "limit": 100}}]},
        "panels": panels,
    }


def annotations_for(out: dict, run_id: str, now_ms: int) -> list[tuple[str, dict]]:
    calls: list[tuple[str, dict]] = []
    for s in out["scenes"]:
        opened = open_locks(s)
        calls.append(("create_annotation", {
            "text": f"{s['id']} {s['severity']} — {s['heading']} — {len(opened)} open locks",
            "tags": ["backlot", f"scene:{s['id']}", f"sev:{s['severity']}", f"run:{run_id}"],
            "time": now_ms,
        }))
        for lk in opened:
            calls.append(("create_annotation", {
                "text": f"{s['id']} {lk['role']} {lk['person'] or '(unassigned)'} s.{lk['section_id']} open",
                "tags": ["backlot", "lock", f"scene:{s['id']}", f"role:{lk['role']}", f"run:{run_id}"],
                "time": now_ms,
            }))
    return calls


async def ensure_datasource() -> None:
    listed = json.loads(await grafana_mcp.call("list_datasources", {}))
    if any(d.get("uid") == DS_UID for d in listed.get("datasources", [])):
        return
    body = json.dumps({"name": "Backlot TestData", "type": DS_TYPE, "uid": DS_UID, "access": "proxy"})
    await grafana_mcp.call("grafana_api_request", {"method": "POST", "endpoint": "/api/datasources", "body": body})


async def publish(out: dict, run_id: str) -> dict:
    await ensure_datasource()
    await grafana_mcp.call("update_dashboard", {"dashboard": build_dashboard(out), "overwrite": True, "message": run_id})
    calls = annotations_for(out, run_id, int(time.time() * 1000))
    results = await grafana_mcp.call_many(calls)
    return {"dashboard_uid": DASH_UID, "annotations": len(results), "run_id": run_id}


def main() -> None:
    today = sys.argv[1] if len(sys.argv) > 1 else "2026-09-05"
    out = _run(DEFAULT_SAMPLES, today)
    run_id = time.strftime("%Y%m%dT%H%M%S")
    print(json.dumps(asyncio.run(publish(out, run_id))))
    print(f"{os.environ.get('GRAFANA_URL', 'http://localhost:3000')}/d/{DASH_UID}")


if __name__ == "__main__":
    main()
