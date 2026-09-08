# Team checklist - Sean & Sehrish

Status reviewed against this checkout on 2026-09-08. Deadline: Sep 9, 2026,
2:00pm PDT.

Judge-ready plan: `docs/JUDGE-READY-PLAN.md`.

## Sean (this repo: rules engine, Gemini, Grafana)

- [x] Current ADK pipeline files exist: `src/main.py`, `src/agent/models.py`, `src/agent/pipeline.py`.
- [x] Saved ADK pipeline fixture exists: `public/output.json`.
- [x] Install/confirm test runner in `.venv`; `pytest` is not currently importable.
- [x] Capture one live Gemini/ADK receipt from the current pipeline and save the exact command, model, date, and output JSON.
- [x] Restore or rebuild the minimum deterministic severity bridge from the ADK hazard tags (`src/engine/safety.py`).
- [x] Restore or rebuild the minimum Grafana MCP publisher. One visible annotation is enough for the first receipt (`src/engine/grafana_client.py`).
- [x] Update README status only with runnable receipts from this checkout.
- [x] Offline demo segment: run from saved fixture with network disabled and show the wall/reader still has the last known result.
- [x] Re-run public-safety pass before final push: no `.env`, API keys, service account JSON, private tokens, or private tooling references.

## Sehrish (front end)

- [x] Contract documented: `docs/ENGINE-JSON-CONTRACT.md`.
- [x] Static fixture exists for zero-Python iteration.
- [x] Build only a hosted reader against the fixture/live JSON: severity badges, department deltas, hazard tags, and Grafana link (`public/index.html`).
- [ ] Deploy the hosted project URL.
- [x] Do not build a second workflow, auth, editor, or dashboard clone before Gemini and Grafana receipts exist.

## Both

- [x] Current Devpost/Grafana public pages reviewed on 2026-09-08 for planning.
- [ ] Read the full Devpost Official Rules before final submission.
- [ ] Google Cloud $100 hackathon credit form, if still useful.
- [ ] 3-minute demo video, public YouTube/Vimeo, English or subtitled. Needs Gemini receipt + Grafana MCP receipt + hosted reader first.
- [ ] Devpost submission form.
- [ ] Confirm MIT license shows in the GitHub repo "About" section.
