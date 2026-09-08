# Universal CallSheet (UCS)
Agentic Cinema Hackathon — Grafana Labs Track

A deterministic, offline-capable safety governance agent for film production. Powered by **Google Cloud Gemini** and **Grafana OSS**, it turns a raw script revision into structured per-department work deltas and hazard tags, runs them through a deterministic safety engine, and routes `RED/STOP` alerts to a self-hosted Grafana wall using the official MCP server.

## Track & Tech Stack
- **Partner:** Grafana Labs (Grafana OSS self-hosted via `grafana/mcp-grafana`)
- **Platform:** Google Cloud Gemini (via official `google-adk` / `google-genai`)
- **Language:** Python
- **Frontend:** Zero-dependency static HTML Hosted Reader HUD

## The Problem
Ninety-five percent of produced films take three or more rewrites before principal photography. A revision lands as colored pages, distributed by hand through the script supervisor. Nothing cascades automatically to props, wardrobe, locations, stunts, or the safety officer. 

The pattern across a decade of set deaths is the same: the work changed, the hazard assessment did not. Alberta's OHS Code says it in one clause (s.7(4)(c)): the hazard assessment must be repeated "when a work process or operation changes." Nobody on a set has a tool that does that.

## Core Proof Path (How it works)
Our system executes a 3-step pipeline to guarantee safety without hallucinations:

1. **Gemini / Google ADK Extraction (`src/agent/pipeline.py`)**
   The agent compares an original scene against a revised scene, outputting strict, schema-bound Pydantic models:
   `DiffOutput` -> `CascadeOutput` -> `HazardTagOutput`
2. **Deterministic Safety Engine (`src/engine/safety.py`)**
   LLMs do not make legal safety decisions. The extracted hazard tags are passed into a pure Python rules engine that enforces Jurisdiction Safety Rules (e.g. Row 2 Pyro + Row 9 Heights = `RED` Severity, triggering mandatory clears).
3. **Grafana MCP Publisher (`src/engine/grafana_client.py`)**
   The deterministic result is published instantly to a local Grafana dashboard using the official `mcp` Python SDK and `uvx mcp-grafana`.

## Project Structure
```
src/main.py                 FastAPI server and orchestrator for analysis and API endpoints
src/agent/pipeline.py       Google ADK Agents for diff, cascade, and hazard tagging
src/agent/models.py         Pydantic schema constraints
src/engine/safety.py        Deterministic non-LLM safety logic (AB OHS Code rules)
src/engine/grafana_client.py Official MCP client for pushing annotations
src/engine/db.py            SQLite persistence layer for run history
public/index.html           Hosted Reader UI HUD (Dark mode, responsive)
public/style.css            Modern cinematic CSS design with responsive media queries
public/app.js               Interactive UI logic, API client, and hazard detail modals
public/output.json          The generated verified result of the pipeline
```

## Running the Engine
This project runs entirely locally.
```bash
# 1. Install dependencies
pip install -e .
# (or pip install -r requirements.txt)

# 2. Add Credentials to .env
GEMINI_API_KEY="your_api_key"
GEMINI_MODEL="gemini-3.7-flash"
GRAFANA_URL="http://localhost:3000"
GRAFANA_API_KEY="glsa_your_token"

# 3. Start the Application & API Server
python src/main.py
# (or: uvicorn src.main:app --host 0.0.0.0 --port 8000)
# Open http://localhost:8000 in your browser
```

## Verification Status

| Component | Status | Proof |
|---|---|---|
| **ADK Pipeline** | VERIFIED | `src/agent/pipeline.py` extracts structure cleanly; tests pass in `src/agent/test_pipeline.py`. |
| **Safety Engine** | VERIFIED | `src/engine/safety.py` deterministically flags `RED` severities (pyro + heights) and mandates required clears. |
| **Grafana MCP** | VERIFIED | `src/engine/grafana_client.py` successfully published annotation to `/d/ucs-safety-wall/universal-callsheet-safety-wall` with runtime receipt in `public/output.json`. |
| **Persistence (SQLite)** | VERIFIED | `src/engine/db.py` records every pipeline execution into local SQLite storage (`data/ucs_history.db`). |
| **Hosted Reader HUD** | VERIFIED | `public/index.html` loads live data via `/api/latest` with interactive hazard inspection modals and fallback cache. |
| **Test Suite** | VERIFIED | `pytest` passes all unit and integration tests cleanly across agent, engine, and MCP. |

## Authors & Team

* **[Sean Morin](https://github.com/deveraux-dev)** ([deveraux.dev](https://deveraux.dev)) — System Architecture, Domain Safety Engineering & OHS Regulatory Philosophy
* **[Sehrish Majeed](https://github.com/sehrishmajeed)** — Agentic AI Implementation, Google ADK Pipeline & Grafana MCP Integration

*Disclaimer: This is a hackathon prototype for safety workflow assistance. It is not legal advice. Final authority remains with production safety leadership and applicable regulators.*
