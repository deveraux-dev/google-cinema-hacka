# Prompt: build `src/agent/publish.py` (engine output → Grafana via MCP)

You are working in a Python 3.11+ repo for the Agentic Cinema hackathon, Grafana Labs track.
Write `src/agent/publish.py`, extend `src/agent/grafana_mcp.py`, and add `tests/test_publish.py`.
Do not touch any other file. Return complete file contents, not diffs.

## What exists (verified)

- `src/agent/harness.py` has `_run(paths: dict[str, Path], today: str) -> dict` and
  `DEFAULT_SAMPLES` (plan/scenes/clears/register sample paths). Reuse it for engine output.
- `src/agent/grafana_mcp.py` talks to the official `mcp-grafana` server over stdio using the
  `mcp` Python package. It exposes `async def call(name: str, args: dict) -> str`, which opens a
  fresh session per call (one process spawn per call). It reads `GRAFANA_URL` and
  `GRAFANA_SERVICE_ACCOUNT_TOKEN` from `.env` via `python-dotenv`. `_params()` builds
  `StdioServerParameters`. Tool results come back as text; JSON results are JSON strings.
- Local Grafana OSS 13.2.1 at `http://localhost:3000`, no dashboards, no datasources.
  Available MCP tools include `create_annotation`, `update_dashboard`, `create_datasource`,
  `list_datasources`, `search_dashboards`, `get_annotations`, `grafana_api_request`.
- Tests use `sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))` at the top
  and run with `pytest -q`. Existing tests mock network; do the same.

## Engine output shape (input to publish)

```json
{"production": "Backlot Test", "jurisdiction": "AB", "today": "2026-09-05",
 "scenes": [{"id": "S1", "heading": "INT. OFFICE - DAY", "day": "D1", "severity": "RED",
   "requirements": [...], "locks": [{"scene_id": "S1", "role": "first_ad", "person": "Ann Frost",
   "section_id": "7", "applied": "", "released": null}],
   "first_aid": {"table": 6, "class": "medium", "band": "close", "headcount_row": "20 – 49",
     "requirement": "1 Basic First Aider | ..."},
   "register": {"first_aider": "expired"}}]}
```

- `severity` is one of `GREEN < AMBER < RED < STOP`.
- A lock is open while `released` is `null`. Sample has 3 scenes with 9, 144, 145 open locks.
- For BC `first_aid` is `{"table": "3-A", "requirement": "...", "unresolved": true}`.

## MCP tool schemas (exact)

`create_annotation` args: `dashboardUid: str`, `panelId: int`, `text: str`, `tags: [str]`,
`time: int` (epoch ms), `timeEnd: int`, `data: object`. None required.

`update_dashboard` args: `dashboard: object` (full dashboard JSON), `overwrite: bool`,
`message: str`, `folderUid: str`. Returns JSON with the saved uid.

`create_datasource` args: `name: str` (required), `type: str` (required), `access: str`,
`isDefault: bool`, `fields: object`, `schemaReviewed: bool`. Note the two-call schema-review
flow: first call returns a field schema, second call with `schemaReviewed: true` provisions.
Handle both, or fall back to `grafana_api_request` with `POST /api/datasources` and body
`{"name": "...", "type": "grafana-testdata-datasource", "uid": "backlot-testdata", "access": "proxy"}`.

`grafana_api_request` args: `method: GET|POST|PUT|PATCH|DELETE`, `endpoint: str` (starts with `/`),
`body: str` (JSON string), `jq: str`.

## Build this

1. In `grafana_mcp.py` add `async def call_many(calls: list[tuple[str, dict]]) -> list[str]`
   that opens ONE session and runs all calls in order. Keep `call` as is.
2. `publish.py`:
   - `ensure_datasource()` → idempotent; uid `backlot-testdata`, type
     `grafana-testdata-datasource`. Check `list_datasources` first.
   - `build_dashboard(out: dict) -> dict` → uid `backlot`, title `Backlot Safety Wall`,
     `schemaVersion` 39, `time: {"from": "now-6h", "to": "now"}`, `refresh: "10s"`. Four panels,
     each using the testdata datasource with `scenarioId: "csv_content"` and a `csvContent`
     string generated from the engine output:
     1. `stat` "Severity per scene": csv `scene,severity` with numeric 0..3; value mappings
        0→GREEN green, 1→AMBER orange, 2→RED red, 3→STOP dark-red; `colorMode: background`,
        `graphMode: none`, `reduceOptions.calcs: ["lastNotNull"]`.
     2. `bargauge` "Open locks per scene": csv `scene,open`.
     3. `table` "First aid (Schedule 2)": csv `scene,table,band,headcount_row,requirement`
        (for BC: `scene,table,band,headcount_row,requirement` with `unresolved` in requirement).
     4. `annolist` "Lock events": `onlyFromThisDashboard: false`, `tags: ["backlot"]`, `limit: 50`.
     Add `annotations.list` entry on the built-in `-- Grafana --` datasource filtered by tag
     `backlot` so events draw on the timeline.
   - `publish(out: dict, run_id: str) -> dict` → calls `ensure_datasource`, then
     `update_dashboard(dashboard=..., overwrite=True, message=run_id)`, then via ONE
     `call_many` creates: one annotation per scene
     (`text: "S1 RED — INT. OFFICE - DAY — 9 open locks"`, tags
     `["backlot", "scene:S1", "sev:RED", f"run:{run_id}"]`) plus one annotation per OPEN lock
     with `text: "S1 first_ad Ann Frost s.7 open"`, tags
     `["backlot", "lock", "scene:S1", "role:first_ad", f"run:{run_id}"]`. Use `time` = now ms.
     Return `{"dashboard_uid": ..., "annotations": <count>, "run_id": run_id}`.
   - `main()`: `python -m agent.publish [today]` → runs `_run(DEFAULT_SAMPLES, today)`,
     publishes, prints the returned dict as JSON, and prints the dashboard URL
     `{GRAFANA_URL}/d/backlot`.
3. `tests/test_publish.py`: mock `grafana_mcp.call` / `call_many` (no network). Assert:
   dashboard has 4 panels with the stated types; severity csv maps STOP→3; annotation count
   equals scenes + open locks for the fixture at `samples/engine.output.json`; tags contain
   `run:<id>`.

## Constraints

- Module header docstring ≤ 3 lines. No explanatory comments restating code.
- No new dependencies. `mcp`, `python-dotenv` already installed.
- No secrets in code. Read env only via the existing `load_dotenv` in `grafana_mcp.py`.
- Every function has type hints. Use `asyncio.run` only in `main()`.
- Deterministic: the same engine output must produce the same dashboard JSON (no timestamps in
  the dashboard; timestamps only in annotations).
