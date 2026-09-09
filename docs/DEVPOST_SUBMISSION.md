# Devpost Submission — Universal CallSheet (UCS)

## Project Title
**Universal CallSheet (UCS)**

## Tagline
Structured AI script revision analysis and deterministic safety governance for film production.

## Demo Video
https://youtu.be/XzUXE0kLOAs

## Track
**Grafana Labs Track** (Agentic Cinema Hackathon)

---

## Inspiration
Ninety-five percent of produced films undergo three or more rewrites before principal photography. A revision arrives as colored pages, distributed by hand through the script supervisor. In fast-paced production environments, changes cascade haphazardly across departments: props, wardrobe, stunts, pyrotechnics, and safety officers rarely receive synchronized updates in time.

The tragedy across a decade of film set accidents and fatalities is consistently identical: **the work changed, but the hazard assessment did not.**

Alberta's Occupational Health and Safety (OHS) Code states it explicitly (s.7(4)(c)): a hazard assessment must be repeated *"when a work process or operation changes."* Yet until now, nobody on a film set had an automated, verifiable tool to identify changes, recalculate department work deltas, and enforce safety compliance across teams in real time.

---

## What It Does
Universal CallSheet (UCS) is an agentic safety governance system for film productions. It closes the dangerous communication gap between script changes and set safety through structured analysis followed by a deterministic safety gate:

1. **Agentic Script Extraction (Google ADK & Gemini):**
   When a new script revision is submitted, our Google ADK agents compare the original scene against the revision, generating structured Pydantic models:
   - **Diff Extraction:** Isolated narrative changes.
   - **Department Cascade:** Specific operational deltas for SPFX, Stunts, Wardrobe, Grip, and Set Dec.
   - **Hazard Tag Extraction:** Identification of regulated hazards (e.g., Pyrotechnics, Heights > 3m, Lockout/Tagout, Powered Mobile Equipment).

2. **Deterministic Safety Engine (No-Hallucination Gate):**
   *LLMs must not make final legal safety decisions.* UCS passes the structured hazard tags into a pure, auditable Python rules engine implementing jurisdiction-specific OHS regulations (Alberta OHS Code). If critical hazards are introduced (e.g., Row 2 Pyro + Row 9 Heights), the engine immediately flags a **`RED / STOP`** severity and mandates required safety clearances (e.g., *SPFX Lead Clear, Stunt Coordinator Clear, Rigger Fall Protection Clear, Equipment Lockout Clear*).

3. **Grafana Annotation via MCP Server:**
   Significant safety results can be published through the official `mcp` Python client and `grafana/mcp-grafana`. The verified local path creates real annotations; hosted MCP is supported but requires a separately deployed endpoint.

4. **Production HUD (Hosted Reader):**
   A sleek, cinematic dark-mode web HUD gives crew members an instant, responsive breakdown of the scene's safety status, required clears, and clickable hazard details, complete with full offline fallback cache capabilities.

---

## How We Built It
- **AI & Agent Orchestration:** Built with the official **`google-adk`** and **`google-genai`** SDKs powered by the configured Gemini model for schema-constrained structured output generation.
- **Deterministic Rules Engine:** Pure Python module with zero LLM dependency to ensure 100% deterministic, rule-bound safety evaluation.
- **Grafana MCP Integration:** Implemented using the official Model Context Protocol (MCP) to publish safety annotations to Grafana OSS dashboards. The local stdio path is verified; hosted Streamable HTTP is supported but requires a separately deployed MCP endpoint.
- **Backend & Persistence:** **FastAPI** asynchronous server with best-effort local SQLite run logging; serverless history is ephemeral.
- **Frontend HUD:** Zero-dependency, responsive HTML/CSS/JavaScript interface styled with a cinematic dark-mode HUD theme and interactive hazard analysis modals.

---

## Challenges We Ran Into
- **Enforcing a deterministic safety boundary:** Generative AI is inherently probabilistic. We solved this with an architectural split: AI handles unstructured natural language extraction into strict Pydantic schemas, while a deterministic rules engine handles all compliance and severity calculations.
- **Sovereign Provenance & Tool Compliance:** Aligning strictly with hackathon tool invariants required eliminating unauthorized tooling dependencies and rebuilding pure Google ADK pipelines from scratch with verifiable test receipts.

---

## Accomplishments We're Proud Of
- **End-to-End Auditable Chain:** A verified local path runs from script revision input through schema-compatible structured analysis or marked fallback, deterministic safety gate, Grafana MCP annotation, and HUD JSON rendering. Live Gemini requires configured credentials and available quota and is reported separately from fallback mode.
- **100% Pass on Automated Test Suite:** Unit and integration tests verify every step of the agent, engine, and MCP client with automated pytest test passes.
- **Credential Boundary:** Gemini and Grafana credentials remain server-side and are never embedded in browser code. Local caches stay in the workspace; serverless storage is treated as ephemeral.

---

## What We Learned
- How to effectively bridge agentic LLM reasoning with deterministic industrial safety standards.
- Deep hands-on experience leveraging the official Google ADK framework and Grafana MCP ecosystem for real-time operations.

---

## What's Next for Universal CallSheet
- **Multi-Jurisdiction Expansion:** Adding automated rule mappings for British Columbia (WorkSafeBC Schedule 3-A), California OSHA, and UK HSE.
- **Live Environmental Integration:** Pulling real-time weather feeds (wind speed, lightning, temperature) into Grafana to trigger automatic safety halts for outdoor crane and pyrotechnic stunts.
- **Real-Time Stage Push Notifications:** Native push alerts directly to crew mobile radios and smart call-sheets on set.
