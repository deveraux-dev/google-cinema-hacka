# 3-Minute Demo Video Script — Universal CallSheet (UCS)

> **Time Limit:** Exactly 3:00 minutes maximum.  
> **Format:** Screen recording with voiceover (public YouTube or Vimeo).  
> **Goal:** Clearly prove the chain: Script Revision -> Gemini ADK -> Deterministic Safety Gate -> Grafana MCP -> Production HUD.

---

### Segment 1: The Problem (0:00 - 0:25)
* **Visual on Screen:** Title card or script revision page with red pen notes / highlighters.
* **Voiceover:**
  > "Ninety-five percent of films undergo multiple script rewrites right before shooting. When a revision lands, changes are distributed manually. Stunts, special effects, and safety officers rarely get the message simultaneously.
  > Across a decade of film set accidents, the story is always the same: *the work changed, but the hazard assessment did not.*
  > This is Universal CallSheet — an agentic safety governance system powered by Google Gemini and Grafana Labs."

---

### Segment 2: Gemini / Google ADK Extraction (0:25 - 1:05)
* **Visual on Screen:** Terminal / IDE showing the script diff: Scene 1 changes from a quiet loading dock to adding a pyrotechnic flash pot, a 20-foot jump, and a hydraulic lift. Running `python src/main.py` or clicking "Run New Analysis Pipeline" in the web UI.
* **Voiceover:**
  > "Watch what happens when a revision is introduced. In Scene 1, a script rewrite adds an explosion near a dumpster, a 20-foot platform jump, and a hydraulic lift reset between takes.
  > We feed this into our Google ADK pipeline powered by the configured Gemini model. 
  > Gemini breaks this down into strict, structured schemas:
  > First, a narrative diff.
  > Second, department deltas for SPFX, Stunts, Grip, and Wardrobe.
  > Third, extracted hazard tags mapped to industrial safety codes."

---

### Segment 3: Deterministic Safety Engine (1:05 - 1:40)
* **Visual on Screen:** Code view of `src/engine/safety.py` showing the pure Python rule evaluation, followed by terminal/UI displaying `SEVERITY: RED`.
* **Voiceover:**
  > "Here is our core engineering principle: **LLMs do not make legal safety decisions.**
  > The extracted tags enter our deterministic Python rules engine, enforcing Alberta's Occupational Health and Safety Code.
  > The engine detects high-risk combinations — pyrotechnics plus heights over three meters.
  > It immediately halts the workflow with a `RED / STOP` severity and mandates five specific safety clearances: SPFX lead clear, stunt coordinator clear, fall protection clear, and equipment lockout clear."

---

### Segment 4: Live Grafana MCP Wall (1:40 - 2:20)
* **Visual on Screen:** Switching browser tab to Grafana dashboard (`http://localhost:3000/d/ucs-safety-wall`). Show the newly added annotation badge appearing on the timeline, detailing the incident and required clears.
* **Voiceover:**
  > "Now, the Grafana integration. Through the official Grafana Model Context Protocol (MCP) server, our agent writes this incident live to the stage's Grafana Incident Wall.
  > Stage managers and safety supervisors see the real-time annotation instantly on their production monitoring board, ensuring nobody calls 'Action!' until every mandatory clear is verified."

---

### Segment 5: Production HUD & Offline Governance (2:20 - 2:45)
* **Visual on Screen:** Switching to the Hosted Reader UI (`http://localhost:8000`). Clicking on the Hazard Tags to demonstrate interactive modals (e.g. Row 2 Pyro, Row 9 Heights), resizing the window to show responsive mobile layout.
* **Voiceover:**
  > "On set, crew members view the lightweight, responsive Universal CallSheet HUD on their phones or tablets.
  > Department leads can click any hazard tag to inspect the exact script reasoning.
  > And because the frontend caches the latest sovereign run, the safety wall remains fully functional offline even if remote connectivity drops on location."

---

### Segment 6: Conclusion (2:45 - 3:00)
* **Visual on Screen:** Summary slide with project links, GitHub repo, and team credits.
* **Voiceover:**
  > "Universal CallSheet bridges the gap between creative script evolution and non-negotiable set safety — powered by Google Gemini, Google ADK, and Grafana Labs. Thank you!"
