<div align="center">
  <img src="assets/ucs-logo.jpg" width="200" alt="UCS Logo">
  <h1>Universal CallSheet (UCS)</h1>
  <p><b>AI-powered Safety Governance for Film Production</b></p>
  
  [![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](#)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](#)
  [![Gemini](https://img.shields.io/badge/Google-Gemini_3.7_Flash-4285F4?style=for-the-badge&logo=google)](#)
  [![Grafana](https://img.shields.io/badge/Grafana-MCP-F46800?style=for-the-badge&logo=grafana)](#)
</div>

---

## 🎬 The Problem: Script Changes Outpace Safety Protocols
Film script rewrites happen faster than safety paperwork can keep up. When high-risk hazards (pyrotechnics, heights, weapons) are added at the last minute without clearing the proper departments, **people get hurt**. A manual safety gap on a busy, fast-moving set is a critical liability.

## 💡 The Solution: Universal CallSheet
**Universal CallSheet (UCS)** acts as an automated safety gate between the writer's room and the production floor. 

It uses Google Gemini to read screenplay diffs, instantly extracts physical hazards, routes them through deterministic Python safety rules (Alberta OHS Code), and publishes immutable safety receipts to a Grafana dashboard—ensuring no dangerous stunt ever bypasses the safety team.

---

## ⚙️ How It Works (The Pipeline)

1. 📝 **LLM Extraction:** Google ADK and Gemini `3.7-flash` extract structured `DiffOutput`, `CascadeOutput`, and `HazardTagOutput` from raw script revisions.
2. 🛑 **Deterministic Gate:** The Python safety engine enforces Alberta OHS Code AR 191/2021 to set a final `GREEN`, `STOP`, or `RED` severity. *The LLM does NOT make the final safety decision.*
3. 📊 **Immutable Logging:** Verified hazard tags and severities are routed to the Grafana MCP server for permanent annotation and monitoring.
4. 🖥️ **Production HUD:** The frontend displays the raw JSON payload, the deterministic safety reasoning, required department clearances, and the Grafana receipt in one single, un-falsifiable view.

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.12+
- Node.js 22+ (for UI testing)

### Installation
```powershell
# 1. Install Python dependencies
python -m pip install -e .

# 2. Run the UCS Backend
python src/main.py
```
*The HUD will be available at `http://localhost:8000`.*

---

## ☁️ Cloud Deployment (Vercel)
The live project is hosted on Vercel at [universal-callsheet.vercel.app](https://universal-callsheet.vercel.app). 

To deploy your own instance, ensure the following environment variables are set:
```env
GEMINI_API_KEY=<your-key>
GEMINI_MODEL=gemini-3.7-flash
GRAFANA_MCP_SERVER_TOKEN=<server-auth-token>
GRAFANA_PUBLIC_URL=https://<grafana-host>
GRAFANA_MCP_URL=https://<hosted-mcp-service>/mcp
```

---

## 🧪 Testing & Validation
We believe in proving our code. UCS includes automated testing for both backend logic and frontend UI.
```powershell
# Run backend pipeline tests
python -m pytest -q

# Run Playwright UI smoke tests
npm ci
$env:PLAYWRIGHT_CHROME_PATH='C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:BASE_URL='http://127.0.0.1:8000/'
npm run test:ui
```

---

## ⚖️ Hackathon Compliance & Transparency
- **Net-New Code:** The frontend UI, FastAPI backend, deterministic rules engine, and ADK pipeline integration were all created natively for this hackathon.
- **Strict Dependencies:** UCS relies strictly on Google ADK, Gemini, Grafana MCP, FastAPI, and Playwright. *No unauthorized LLMs were used.*
- **Honest Fallbacks:** Our architecture natively supports a deterministic `offline_fallback` mode if the Gemini API is unreachable, ensuring no "hallucinated" safety checks ever occur.
- **Limitations:** The live Vercel environment uses a placeholder URL for the Grafana MCP endpoint. Serverless execution is ephemeral.

> **Disclaimer:** UCS is a hackathon prototype for safety workflow assistance. It is not legal advice and does not replace production safety leadership, qualified workers, or regulatory authorities.
