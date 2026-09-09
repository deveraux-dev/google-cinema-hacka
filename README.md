# Universal CallSheet (UCS)

Film script rewrites can change the work faster than safety paperwork changes with
it. UCS turns a revised scene into structured production deltas, routes hazards
through a deterministic safety gate, and shows the result in a simple production
HUD.

Built for the Agentic Cinema Hackathon, Grafana Labs track.

## What Judges Should See

One concrete workflow:

1. A scene revision introduces pyrotechnics, a performer fall, firearms, confined
   space, or powered equipment resets.
2. The Google ADK + Gemini pipeline produces structured AI analysis:
   `DiffOutput -> CascadeOutput -> HazardTagOutput`.
3. The Python safety engine owns the final severity decision. The model does not
   decide whether camera may roll.
4. The HUD displays the scene, hazards, required clears, statutory citations, raw
   JSON payload, and Grafana publish receipt.

## Current Verification Ledger

| Area | Status | Receipt |
| --- | --- | --- |
| Frontend HUD | Verified locally | Served by FastAPI from `public/`; defensive static and embedded fallback paths exist. |
| Backend API | Verified locally | `GET /api/context`, `GET /api/scenarios`, `POST /api/analyze`, and `GET /api/latest` import and run. |
| Structured AI analysis | Supported, fallback-safe | Uses Google ADK/Gemini when installed and configured; otherwise returns schema-compatible offline fallback output. |
| Safety engine | Tested locally | `engine.safety.evaluate_safety` returns deterministic severity and required clears from hazard rows. |
| Grafana MCP | Config/client path present | Uses official `grafana/mcp-grafana` through MCP. Live publish requires local Grafana credentials and is reported truthfully in the JSON response. |
| Test suite | Passing | `python -m pytest -q` passes on this branch after the latest fixes. |

## Run Locally

```powershell
python -m pip install -e .
python src/main.py
```

Open:

```text
http://localhost:8000
```

Run tests:

```powershell
python -m pytest -q
```

Run the browser HUD smoke test after the server is running:

```powershell
npm install
$env:PLAYWRIGHT_CHROME_PATH='C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:BASE_URL='http://127.0.0.1:8000/'
npm run test:ui
```

The frontend can still render from `public/output.json` if the API is unavailable
when served from a local web server. It also includes a final embedded demo receipt
if both API and JSON fetch fail.

## Optional Live Services

Gemini / Google ADK:

```text
GEMINI_API_KEY=<your key>
GEMINI_MODEL=<configured Gemini model>
```

Grafana MCP:

```text
GRAFANA_URL=http://localhost:3000
GRAFANA_SERVICE_ACCOUNT_TOKEN=<service account token>
GRAFANA_MCP_COMMAND=uvx
GRAFANA_MCP_ARGS=mcp-grafana
```

Check the Grafana MCP adapter config without starting Grafana:

```powershell
$env:PYTHONPATH='src'
python -m agent.grafana_mcp --check-config
```

## Architecture

```text
Revised scene
  -> Google ADK/Gemini structured AI analysis
  -> Pydantic schemas
  -> deterministic Python safety engine
  -> FastAPI JSON response
  -> production HUD
  -> optional Grafana MCP annotation
```

The important boundary: AI extracts structured facts from the script. Python rules
make the safety decision.

## Repo Boundary

This repository is public hackathon work. Do not commit API keys, service account
JSON, `.env` files, private scripts, or unsupported claims.

## Disclaimer

UCS is a hackathon prototype for safety workflow assistance. It is not legal advice
and does not replace production safety leadership, qualified workers, or regulators.
