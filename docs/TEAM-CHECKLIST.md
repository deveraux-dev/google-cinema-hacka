# Team checklist — Sean & Sherish

Status as of commit `c9982c7`. Deadline: Sep 9, 2026, 2:00pm PDT.

## Sean (this repo: rules engine, Gemini, Grafana)

- [x] Phase A — rules engine: model, routing, first_aid, register, locks,
      engine (`run`/`replay`), samples. 29/29 tests passing.
- [x] `src/agent/gemini_client.py` — minimal `call_gemini(prompt)`, mocked
      tests pass (haiku placeholder, no real key needed to prove the wiring).
- [ ] Drop in a real `GEMINI_API_KEY` in `.env` and make **one real Gemini
      call** — this is the runtime receipt judging requires, not just an import.
- [ ] Wire `call_gemini` into whatever actually needs Gemini for the demo
      (video narration script, or the diff/cascade/tag steps — decide which).
- [ ] Grafana publish: push `engine.run()` output to Grafana via
      `agent.grafana_mcp` (`create_incident` for RED/STOP scenes,
      `create_annotation` per lock). `create_incident` probed once against
      local Grafana OSS — came back with an empty-fields response, meaning
      the Incident app likely isn't available on this OSS instance. Needs
      a real check before relying on it; annotations-only may be the fallback.
- [ ] `grafana/backlot.dashboard.json` — four panels (severity per scene,
      open locks, first aid requirement, on-call), imported via `update_dashboard`.
      VERIFY its schema first (not done yet).
- [ ] README "Status" section: replace with actual runtime receipts once the
      above produce real output (incident IDs, annotation counts, replay proof).
- [ ] Offline demo segment: run with network disabled, confirm engine output
      is identical and Grafana (local) still updates.
- [ ] Public-safety pass before final push: no API keys, no service account
      JSON, `.env` never committed (currently clean — keep it that way).

## Sherish (front end)

- [x] Contract documented: `docs/ENGINE-JSON-CONTRACT.md` — full field
      reference for `engine.run()`'s output (severity ladder, Requirement,
      Lock, first_aid, register shapes).
- [x] Static fixture to build against with zero Python:
      `samples/engine.output.json` (3 sample scenes: S1 RED, S2 STOP, S3 STOP).
- [x] Live local harness for iterating: `$env:PYTHONPATH='src';
      .venv\Scripts\python.exe -m agent.harness [port] [today]` → `GET http://127.0.0.1:8787/engine.json`,
      CORS-open, recomputes fresh each request.
- [ ] Build the web app against the fixture/harness (severity badges, lock
      list, first-aid panel, register status).
- [ ] Decide what "hosted project URL" points to (Vercel, per README) and
      deploy it.
- [ ] Once Sean's Grafana wall exists, decide whether the web app also embeds
      or links to the Grafana dashboard, or stays a separate view of the same
      JSON — not decided yet.

## Both

- [ ] Read the full Devpost Official Rules for Grafana track eligibility
      (checklist item, not yet done by either of us).
- [ ] Google Cloud $100 hackathon credit form (resources page).
- [ ] 3-minute demo video, public YouTube/Vimeo, English or subtitled —
      needs both halves working first (engine + wall + web app).
- [ ] Devpost submission form.
- [ ] Confirm MIT license shows in the GitHub repo "About" section.
