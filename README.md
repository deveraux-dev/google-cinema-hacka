# Universal CallSheet (UCS)

## What it does
AI extracts script changes into hazard rows, deterministic Python rules decide if camera can roll, and Grafana publishes the receipt—all visible in a single-screen production HUD.

## Why it matters
Film script rewrites happen faster than safety paperwork can keep up. When high-risk hazards (pyrotechnics, heights, weapons) are added at the last minute without clearing the proper departments, people get hurt. A manual safety gap on a busy set is a critical liability.

## How it works
1. **LLM Extraction:** Google ADK and Gemini extract structured `DiffOutput`, `CascadeOutput`, and `HazardTagOutput` from the script revision.
2. **Deterministic Gate:** The Python safety engine enforces Alberta OHS Code AR 191/2021 to set a final `GREEN`, `STOP`, or `RED` severity. The LLM does *not* make the safety decision.
3. **Sponsor Integration:** Only verified hazard tags and severities are routed to the Grafana MCP server for annotation.
4. **Reader Output:** The production HUD displays the raw JSON payload, the determinisic reason, required clearances, and the Grafana receipt in one path.

## Built with
- **Google ADK & Gemini 3.7 Flash:** For structured data extraction.
- **Python & FastAPI:** For the deterministic safety gate and backend API.
- **Grafana MCP:** For publishing safety annotations.
- **HTML/CSS/JS:** Vanilla frontend for the HUD.
- **Vercel:** Live serverless deployment.

## How to run

### Cloud Deployment
The live project is hosted on Vercel at [https://universal-callsheet.vercel.app](https://universal-callsheet.vercel.app). 
The Vercel environment requires these exact variables:
```text
GEMINI_API_KEY=<your key>
GEMINI_MODEL=gemini-3.7-flash
GRAFANA_MCP_SERVER_TOKEN=<server-auth-token>
GRAFANA_PUBLIC_URL=https://<grafana-host>
GRAFANA_MCP_URL=https://<hosted-mcp-service>/mcp
```

### Local Development
```powershell
python -m pip install -e .
python src/main.py
```
Open `http://localhost:8000`.

To run the UI test suite:
```powershell
npm install
$env:PLAYWRIGHT_CHROME_PATH='C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:BASE_URL='http://127.0.0.1:8000/'
npm run test:ui
```

## Proof/receipts
- **Hosted URL:** [https://universal-callsheet.vercel.app](https://universal-callsheet.vercel.app)
- **JSON Payload:** The raw ADK extraction and deterministic gate output is viewable directly in the live HUD by clicking `<> RAW JSON`.
- **Test Results:** `python -m pytest -q` passes locally.

## Limitations
- **Grafana Endpoint:** The live Vercel environment uses a placeholder URL for the Grafana MCP endpoint until a real public Grafana instance is provisioned. The backend acknowledges the configuration but cannot successfully publish annotations to the placeholder.
- **Persistence:** Vercel serverless execution is ephemeral. Local SQLite history is not maintained between API calls in production; the live POST response is the source of truth.
- **Jurisdiction:** Only Alberta OHS Code (AR 191/2021) rules are encoded.

## Compliance
- **Net-new:** The frontend UI, FastAPI backend, deterministic rules engine, and ADK pipeline integration were created for this hackathon.
- **Dependencies:** Google ADK, Gemini, Grafana MCP, FastAPI, Playwright.
- **Excluded:** User authentication, historical database retrieval in production, and actual external messaging routing.
- **Claims:** UCS is a hackathon prototype for safety workflow assistance. It is not legal advice and does not replace production safety leadership, qualified workers, or regulators.
