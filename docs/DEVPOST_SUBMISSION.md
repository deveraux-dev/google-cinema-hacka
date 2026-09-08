# Devpost Submission — Universal CallSheet (UCS)

## Project Title
**Universal CallSheet (UCS)**

## Tagline
Deterministic script revision cascades and offline safety governance for film production.

## Track
**Grafana Labs Track** (Agentic Cinema Hackathon)

---

## Inspiration
Ninety-five percent of produced films undergo three or more rewrites before principal photography. A revision arrives as colored pages, distributed by hand through the script supervisor. In fast-paced production environments, changes cascade haphazardly across departments: props, wardrobe, stunts, pyrotechnics, and safety officers rarely receive synchronized updates in time.

The tragedy across a decade of film set accidents and fatalities is consistently identical: **the work changed, but the hazard assessment did not.**

Alberta's Occupational Health and Safety (OHS) Code states it explicitly (s.7(4)(c)): a hazard assessment must be repeated *"when a work process or operation changes."* Yet until now, nobody on a film set had an automated, verifiable tool to identify changes, recalculate department work deltas, and enforce safety compliance across teams in real time.

---

## What It Does
Universal CallSheet (UCS) is an intelligent, deterministic safety governance system for film productions. It closes the dangerous communication gap between script changes and set safety through a 3-step sovereign pipeline:

1. **Agentic Script Extraction (Google ADK & Gemini):**
   When a new script revision is submitted, our Google ADK agents compare the original scene against the revision, generating structured Pydantic models:
   - **Diff Extraction:** Isolated narrative changes.
   - **Department Cascade:** Specific operational deltas for SPFX, Stunts, Wardrobe, Grip, and Set Dec.
   - **Hazard Tag Extraction:** Identification of regulated hazards (e.g., Pyrotechnics, Heights > 3m, Lockout/Tagout, Powered Mobile Equipment).

2. **Deterministic Safety Engine (No-Hallucination Gate):**
   *LLMs must not make final legal safety decisions.* UCS passes the structured hazard tags into a pure, auditable Python rules engine implementing jurisdiction-specific OHS regulations (Alberta OHS Code). If critical hazards are introduced (e.g., Row 2 Pyro + Row 9 Heights), the engine immediately flags a **`RED / STOP`** severity and mandates required safety clearances (e.g., *SPFX Lead Clear, Stunt Coordinator Clear, Rigger Fall Protection Clear, Equipment Lockout Clear*).

3. **Grafana Incident Wall via MCP Server:**
   The deterministic safety status is immediately pushed to a self-hosted Grafana Incident Wall using the official `mcp` Python client and `grafana/mcp-grafana`. Annotations and alerts are rendered in real time for stage managers, safety officers, and department heads.

4. **Production HUD (Hosted Reader):**
   A sleek, cinematic dark-mode web HUD gives crew members an instant, responsive breakdown of the scene's safety status, required clears, and clickable hazard details, complete with full offline fallback cache capabilities.

---

## How We Built It
- **AI & Agent Orchestration:** Built with the official **`google-adk`** and **`google-genai`** SDKs powered by **Gemini 3.7 Flash** for high-precision, schema-constrained structured output generation.
- **Deterministic Rules Engine:** Pure Python module with zero LLM dependency to ensure 100% deterministic, rule-bound safety evaluation.
- **Grafana MCP Integration:** Implemented using the official Model Context Protocol (MCP) to publish real-time alerts and annotations to Grafana OSS dashboards.
- **Backend & Persistence:** **FastAPI** asynchronous server with **SQLite** persistent run logging.
- **Frontend HUD:** Zero-dependency, responsive HTML/CSS/JavaScript interface styled with a cinematic dark-mode HUD theme and interactive hazard analysis modals.

---

## Challenges We Ran Into
- **Enforcing Determinism in an AI World:** Generative AI is inherently probabilistic. In life-critical safety governance, probabilistic output is unacceptable. We solved this with an architectural split: AI handles unstructured natural language extraction into strict Pydantic schemas, while a deterministic rules engine handles all compliance and severity calculations.
- **Sovereign Provenance & Tool Compliance:** Aligning strictly with hackathon tool invariants required eliminating unauthorized tooling dependencies and rebuilding pure Google ADK pipelines from scratch with verifiable test receipts.

---

## Accomplishments We're Proud Of
- **End-to-End Auditable Chain:** Successfully demonstrating a verified path from raw script revision to Gemini extraction, deterministic safety gate, Grafana MCP annotation, and live HUD update in seconds.
- **100% Pass on Automated Test Suite:** Unit and integration tests verify every step of the agent, engine, and MCP client with automated pytest test passes.
- **Zero-Cloud-Retention Architecture:** All historical runs and local caches stay on-premises/in-workspace, preserving confidentiality for pre-release scripts.

---

## What We Learned
- How to effectively bridge agentic LLM reasoning with deterministic industrial safety standards.
- Deep hands-on experience leveraging the official Google ADK framework and Grafana MCP ecosystem for real-time operations.

---

## What's Next for Universal CallSheet
- **Multi-Jurisdiction Expansion:** Adding automated rule mappings for British Columbia (WorkSafeBC Schedule 3-A), California OSHA, and UK HSE.
- **Live Environmental Integration:** Pulling real-time weather feeds (wind speed, lightning, temperature) into Grafana to trigger automatic safety halts for outdoor crane and pyrotechnic stunts.
- **Real-Time Stage Push Notifications:** Native push alerts directly to crew mobile radios and smart call-sheets on set.
