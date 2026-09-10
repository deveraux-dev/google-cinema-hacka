# Team checklist - collaborator and repository owner

Status reviewed against this checkout on 2026-09-08. Deadline: Sep 9, 2026,
2:00pm PDT.

Judge-ready plan: `docs/JUDGE-READY-PLAN.md`.

## Collaborator lane - current implementation and submission

- [x] Current ADK/Gemini pipeline files exist: `src/main.py`, `src/agent/models.py`, `src/agent/pipeline.py`.
- [x] Saved ADK pipeline fixture exists: `public/output.json`.
- [x] Install/confirm test runner in `.venv`; `pytest` is not currently importable.
- [x] Capture and preserve a schema-compatible ADK pipeline result with its runtime mode labeled in the output; live Gemini requires configured credentials and quota.
- [x] Integrate the deterministic severity gate from ADK hazard tags (`src/engine/safety.py`).
- [x] Integrate the Grafana MCP publisher and label receipt state honestly (`src/engine/grafana_client.py`).
- [x] Update README status only with runnable receipts from this checkout.
- [x] Offline demo segment: run from saved fixture with network disabled and show the wall/reader still has the last known result.
- [x] Re-run public-safety pass before final push: no `.env`, API keys, service account JSON, private tokens, or private tooling references.

## Collaborator lane - product and deployment

- [x] Contract documented: `docs/ENGINE-JSON-CONTRACT.md`.
- [x] Static fixture exists for zero-Python iteration.
- [x] Build only a hosted reader against the fixture/live JSON: severity badges, department deltas, hazard tags, and Grafana link (`public/index.html`).
- [x] Deploy and verify the hosted project URL (`https://universal-callsheet.vercel.app`).
- [x] Do not build a second workflow, auth, editor, or dashboard clone before Gemini and Grafana receipts exist.

## Repository owner lane

- [x] Upstream production-safety foundation and jurisdiction data remain represented in `src/` and `data/`.
- [x] Original repository Gemini/Grafana groundwork is preserved in the current implementation history.
- [ ] Final repository visibility change: make the GitHub repository public before submission.

## Shared submission checks

- [x] Current Devpost/Grafana public pages reviewed on 2026-09-08 for planning.
- [ ] Read the full Devpost Official Rules before final submission.
- [ ] Google Cloud $100 hackathon credit form, if still useful.
- [ ] 3-minute demo video, public YouTube/Vimeo, English or subtitled. Needs Gemini receipt + Grafana MCP receipt + hosted reader first.
- [ ] Devpost submission form.
- [ ] Confirm MIT license shows in the GitHub repo "About" section.
