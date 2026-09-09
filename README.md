# Universal CallSheet (UCS)

> **AI can identify what changed in a screenplay; deterministic safety rules decide whether the camera may roll; Grafana receives the receipt only after that gate.**

UCS is a proof-first production safety workflow for 1st ADs and safety leads. It turns a last-minute scene revision into a clear decision, required sign-offs, and an auditable result.

## Why it matters

Film revisions can change physical work faster than safety paperwork changes. UCS makes the change visible before the next take and keeps final safety authority in deterministic rules and designated personnel.

## The Judge Path

1. Select the dangerous S1 or S2 revision, or paste a custom scene.
2. Auto-review can submit the selected revision without another click.
3. Google ADK/Gemini produces structured analysis in the order `DiffOutput -> CascadeOutput -> HazardTagOutput`.
4. The deterministic Python safety engine owns `GREEN`, `RED`, or `STOP`.
5. Only the post-gate result is sent to Grafana MCP, with a visible annotation receipt when configured.
6. The HUD shows changed text, decision, next action, evidence, JSON, and provenance.

The important demo behavior is the refusal: a firearm or other critical hazard reaches `STOP` before a camera-roll decision can be treated as clear.

### What a judge can verify in one pass

- **Problem:** a screenplay revision can introduce physical risk after a call sheet is already in motion.
- **Action:** select S2 and leave Auto-review on; the review submits automatically.
- **Decision:** the deterministic safety engine returns `STOP` and names the required clearances.
- **Proof:** the HUD renders the changed text, hazard tags, JSON contract, runtime chain, and Grafana receipt state.
- **Boundary:** Gemini structures the revision; Python owns the safety decision; Grafana receives only the post-gate event.

The interface labels live requests, history receipts, static snapshots, and embedded fallback data separately. A fallback is a usable demo state, not evidence of a live Gemini or Grafana call.

## What is autonomous

Auto-review is bounded automation, not unrestricted agent authority. With the toggle on, selecting a scenario triggers the existing `/api/analyze` workflow. The backend still validates the structured result, runs deterministic safety rules, and publishes Grafana only after the gate. Users can turn Auto-review off and run a review manually.

## How it works

1. **Structured AI analysis:** Google ADK and Gemini extract `DiffOutput`, `CascadeOutput`, and `HazardTagOutput`.
2. **Deterministic gate:** Python safety rules enforce the encoded Alberta OHS hazard matrix. The model does not decide whether camera may roll.
3. **Sponsor integration:** Only verified hazard tags and severity are routed to the Grafana MCP adapter.
4. **Proof reader:** The HUD displays the revision diff, hazards, clearances, statutory basis, JSON, chain, and receipt state.

## Claim Ledger

| Claim | Status | Evidence |
| --- | --- | --- |
| Structured screenplay analysis | Tested / fallback-safe | Google ADK pipeline and schema tests; offline fallback is labeled in the HUD. |
| Safety decision | Tested | `engine.safety.evaluate_safety` is the decision owner; refusal paths are covered by tests. |
| Auto-review | Tested | UI and API tests verify `trigger: auto_review` and the automatic S2 `STOP` path. |
| Local Grafana MCP | Verified locally | Official `mcp-grafana` stdio transport created real annotations during local verification. |
| Hosted Grafana MCP | Supported / unverified | Streamable HTTP configuration exists, but no hosted MCP receipt is claimed here. |
| Vercel runtime | Supported / environment-dependent | FastAPI import and Vercel-safe paths are implemented; hosted MCP remains an external dependency. |

## Built with

- Google ADK and Gemini for structured extraction.
- Python, FastAPI, Pydantic, and deterministic safety rules.
- Official Grafana MCP over local stdio or hosted Streamable HTTP.
- Vanilla HTML/CSS/JavaScript proof reader.
- Vercel-compatible FastAPI routing.

## Run locally

```powershell
python -m pip install -e .
python -m uvicorn src.main:app --host 127.0.0.1 --port 8003
```

Open `http://127.0.0.1:8003/`.

Run backend tests:

```powershell
python -m pytest -q
```

Run browser tests with installed Chrome:

```powershell
npm install
$env:PLAYWRIGHT_CHROME_PATH='C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:BASE_URL='http://127.0.0.1:8003/'
npm run test:ui
```

## Two-Minute Demo

The complete recording plan, exact narration, truthful fallback wording, and export checklist are in [docs/DEMO_VIDEO_SCRIPT.md](docs/DEMO_VIDEO_SCRIPT.md).

1. Open the scenario deck and leave **Auto-review ON**.
2. Select S2, the confined-space firearm revision.
3. Show the automatic chain: structured analysis, safety engine, Grafana status, frontend receipt.
4. Point to `STOP`, the reason, and pending clearances.
5. Open revision evidence and raw JSON.
6. Explain the boundary: Gemini interprets the revision; Python decides the safety state; Grafana records the post-gate receipt.

## Environment

Keep all values server-side. The browser reads only the JSON response; it never receives these credentials.

Gemini:

```text
GEMINI_API_KEY=<server-side key>
GEMINI_MODEL=gemini-3.7-flash
```

Hosted Grafana MCP:

```text
GRAFANA_MCP_URL=https://<hosted-mcp-service>/mcp
GRAFANA_MCP_SERVER_TOKEN=<server-side token>
GRAFANA_PUBLIC_URL=https://<grafana-host>
GRAFANA_MCP_TIMEOUT_SECONDS=20
```

Never expose these variables as browser or `NEXT_PUBLIC_*` variables.

For Vercel, configure the same variables in the project environment settings and deploy the `frontend-deploy` branch. A hosted `GRAFANA_MCP_URL` is required for production MCP publishing; local stdio is not available inside Vercel serverless functions.

## Limitations

- Local stdio Grafana MCP is verified. Hosted MCP is supported but remains unverified until a real hosted endpoint returns a receipt.
- Vercel serverless SQLite history is ephemeral; the live POST response is the source of truth.
- Only the encoded Alberta OHS hazard rules are covered.
- UCS is an assistive hackathon prototype, not legal advice or a replacement for qualified safety leadership or regulators.

## Compliance and provenance

This repository contains new UCS implementation work. It does not copy private implementation code, credentials, receipts, or assets from other projects. The transferable pattern is the proof architecture: AI proposes or extracts, deterministic code gates, the external tool receives only cleared output, and the UI shows the receipt.
