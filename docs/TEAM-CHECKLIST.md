# Team checklist — Sean & Sehrish

Status as of commit `c9982c7`. Deadline: Sep 9, 2026, 2:00pm PDT.

## Sean (this repo: rules engine, Gemini, Grafana)

- [x] Phase A — rules engine: model, routing, first_aid, register, locks,
      engine (`run`/`replay`), samples. 29/29 tests passing.
- [x] `src/agent/gemini_client.py` — minimal `call_gemini(prompt)`, mocked
      tests pass (haiku placeholder, no real key needed to prove the wiring).
- [x] `src/agent/main.py` — engine → publish → Gemini crew brief. Runs without
      a key (brief skipped, wall still published).
- [ ] **Sehrish's key**: put `GEMINI_API_KEY` in `.env`, `pip install google-genai`,
      run `python -m agent.main` and paste the `gemini_brief` output into the
      README Status table. That is the Gemini runtime receipt.
- [x] Grafana publish: `src/agent/publish.py` — `update_dashboard` (uid
      `backlot`, 4 panels on a testdata csv datasource) + one `create_annotation`
      per scene and per open lock in a single MCP session. Ran live: 301
      annotations, dashboard queryable. Incidents dropped (not on OSS).
- [x] README "Status" section carries the runtime receipts.
- [ ] Offline demo segment (video only): wifi off on camera, `python -m agent.main`,
      refresh the wall. No Gemma claim anywhere; README/ARCHITECTURE softened.
- [x] Public-safety pass 2026-09-07: no `.env` ever committed, no key/token/private-key
      patterns in tracked files or full history, no private-tooling references.
      Re-run before the final push.

## Sehrish (front end)

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
