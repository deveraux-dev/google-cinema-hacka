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
| Structured AI analysis | Supported, fallback-safe | `google-adk` imports after dependency install; no Gemini key was present in this shell, so runtime used `offline_structured_fallback`. |
| Safety engine | Tested locally | `engine.safety.evaluate_safety` returns deterministic severity and required clears from hazard rows. |
| Grafana MCP | Verified locally; hosted transport supported | Grafana OSS `13.0.2` was healthy on `localhost:3000`; official `uvx mcp-grafana` `v1.3.0` created local annotations, including ids `30-36`. Streamable HTTP is supported by the client but has no hosted endpoint in this repo. |
| Frontend/backend/Grafana receipt | Verified locally | Browser loaded backend JSON and displayed `Analysis: offline structured fallback`, `Safety Engine: RED`, `Grafana MCP: Published`, `Frontend JSON: Rendered JSON`. |
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

For Vercel, run the official `mcp-grafana` server separately with Streamable HTTP
and set these server-side variables. Never expose them as `NEXT_PUBLIC_*` or other
browser variables:

```text
GRAFANA_MCP_URL=https://<hosted-mcp-service>/mcp
GRAFANA_MCP_SERVER_TOKEN=<server-auth-token-if-enabled>
GRAFANA_PUBLIC_URL=https://<grafana-host>
GRAFANA_MCP_TIMEOUT_SECONDS=20
```

Vercel detects the FastAPI application through `src.main:app` in `pyproject.toml`
and serves the HUD from `public/` under the same origin. Add `GEMINI_API_KEY` and
the Grafana variables in Vercel Project Settings as encrypted server environment
variables. `GRAFANA_MCP_URL` is supported, but no hosted MCP service is claimed as
live until its URL and receipt are supplied.

The deployed function does not write the repository's `public/output.json`; the
live POST response is the source of truth. SQLite history is best-effort and
ephemeral in serverless execution. The UI labels cached data as a snapshot.

Local Grafana basic auth is also supported by `mcp-grafana`:

```text
GRAFANA_USERNAME=admin
GRAFANA_PASSWORD=admin
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

The important boundary: AI extracts structured facts from the script when Gemini
credentials are present. Python rules make the safety decision. Without Gemini
credentials, the app uses a schema-compatible offline fallback and marks that mode
in the JSON and HUD.

## Repo Boundary

This repository is public hackathon work. Do not commit API keys, service account
JSON, `.env` files, private scripts, or unsupported claims.

## Disclaimer

UCS is a hackathon prototype for safety workflow assistance. It is not legal advice
and does not replace production safety leadership, qualified workers, or regulators.
