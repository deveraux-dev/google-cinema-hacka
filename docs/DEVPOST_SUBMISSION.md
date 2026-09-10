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
Film productions often work through multiple rewrites before principal photography. A revision arrives as colored pages, distributed by hand through the script supervisor. In fast-paced production environments, changes cascade across departments: props, wardrobe, stunts, pyrotechnics, and safety officers may not receive synchronized updates in time.

The tragedy across a decade of film set accidents and fatalities is consistently identical: **the work changed, but the hazard assessment did not.**

Alberta's Occupational Health and Safety (OHS) Code states it explicitly (s.7(4)(c)): a hazard assessment must be repeated *"when a work process or operation changes."* UCS provides a focused, verifiable workflow to identify changes, recalculate department work deltas, and surface the safety action before the next take.

---

## What It Does
Universal CallSheet (UCS) is an agentic safety governance system for film productions. It closes the dangerous communication gap between script changes and set safety through structured analysis followed by a deterministic safety gate:

1. **Agentic Script Extraction (Google ADK & Gemini):**
   When a new script revision is submitted, our Google ADK agents compare the original scene against the revision, generating structured Pydantic models:
   - **Diff Extraction:** Isolated narrative changes.
   - **Department Cascade:** Specific operational deltas for SPFX, Stunts, Wardrobe, Grip, and Set Dec.
   - **Hazard Tag Extraction:** Identification of regulated hazards (e.g., Pyrotechnics, Heights > 3m, Lockout/Tagout, Powered Mobile Equipment).

2. **Deterministic Safety Engine (No-Hallucination Gate):**
   *LLMs must not make final legal safety decisions.* UCS passes the structured hazard tags into a pure, auditable Python rules engine implementing the governed Alberta OHS model. A firearm hazard is mapped to **`STOP`** in the current rule table; other governed hazards can produce **`REVIEW`** or **`RED`** and mandate the corresponding safety clearances.

3. **Grafana Annotation via MCP Server:**
   Significant safety results can be published through the official `mcp` Python client and `grafana/mcp-grafana`. The verified local path creates real annotations; hosted MCP is supported but requires a separately deployed endpoint.

4. **Production HUD (Hosted Reader):**
   A responsive dark-mode web HUD gives crew members a clear breakdown of the scene's safety status, required clearances, and clickable hazard details. When the provider is unavailable, the app uses a clearly labeled schema-compatible fallback.

---

## How We Built It
- **AI & Agent Orchestration:** Built with the official **`google-adk`** and **`google-genai`** SDKs for schema-constrained structured output when Gemini credentials and quota are available.
- **Deterministic Rules Engine:** Pure Python module with zero LLM dependency to ensure 100% deterministic, rule-bound safety evaluation.
- **Grafana MCP Integration:** Implemented using the official Model Context Protocol (MCP) to publish safety annotations to Grafana OSS dashboards. The local stdio path is verified; hosted Streamable HTTP is supported but requires a separately deployed MCP endpoint.
- **Backend & Persistence:** **FastAPI** asynchronous server with best-effort local SQLite run logging; serverless history is ephemeral.
- **Frontend HUD:** Zero-dependency, responsive HTML/CSS/JavaScript interface styled as a production review cockpit with interactive hazard and statutory evidence panels.

---

## Challenges We Ran Into
- **Enforcing a deterministic safety boundary:** Generative AI is inherently probabilistic. We solved this with an architectural split: AI handles unstructured natural language extraction into strict Pydantic schemas, while a deterministic rules engine handles all compliance and severity calculations.
- **Truthful provenance:** Live requests, structured fallback, static snapshots, and Grafana receipt state are labeled separately so the interface does not turn a supported path into an unverified claim.

---

## Accomplishments We're Proud Of
- **End-to-End Auditable Chain:** A verified local path runs from script revision input through schema-compatible structured analysis or marked fallback, deterministic safety gate, Grafana MCP annotation, and HUD JSON rendering. Live Gemini requires configured credentials and available quota and is reported separately from fallback mode.
- **Automated regression coverage:** Backend tests cover the API, agent pipeline, safety engine, database, and Grafana client. The browser suite covers responsive rendering, S2 auto-review, custom revisions, navigation, and the non-overridable `STOP` gate.
- **Credential Boundary:** Gemini and Grafana credentials remain server-side and are never embedded in browser code. Local caches stay in the workspace; serverless storage is treated as ephemeral.

---

## What We Learned
- How to effectively bridge agentic LLM reasoning with deterministic industrial safety standards.
- Practical experience connecting Google ADK structured analysis to deterministic rules and a Grafana MCP receipt path.

---

## What's Next for Universal CallSheet
- **Multi-Jurisdiction Expansion:** Adding automated rule mappings for British Columbia (WorkSafeBC Schedule 3-A), California OSHA, and UK HSE.
- **Live Environmental Integration:** Pulling real-time weather feeds (wind speed, lightning, temperature) into Grafana to trigger automatic safety halts for outdoor crane and pyrotechnic stunts.
- **Real-Time Stage Push Notifications:** Native push alerts directly to crew mobile radios and smart call-sheets on set.
