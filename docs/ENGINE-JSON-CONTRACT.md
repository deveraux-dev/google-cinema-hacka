# Engine JSON contract (for Sherish's web app)

The rules engine (`src/agent/engine.py:run`) is the only thing the front end needs
to read. It takes a production plan, scene list, clears, and crew register and
returns one JSON object — deterministic, same input always gives the same output
(`engine.replay` runs it twice and asserts byte-identical).

CLI to produce it yourself (`PYTHONPATH=src` is required unless you ran `pip install -e .`):
```
$env:PYTHONPATH='src'; .venv\Scripts\python.exe -m agent.engine samples/production.plan.json samples/scenes.json samples/clears.json samples/crew.csv 2026-09-05
```

## For Sherish: two ways to get this without touching Python

1. **Static fixture** — `samples/engine.output.json`, checked into the repo, is
   the exact output of the CLI above on the sample production. Fetch/import it
   directly for building the UI against real shapes. It won't change unless
   someone regenerates it.
2. **Local harness (live)** — run
   `$env:PYTHONPATH='src'; .venv\Scripts\python.exe -m agent.harness [port] [today]` (defaults
   `8787`, `2026-09-05`) and `GET http://127.0.0.1:8787/engine.json` returns
   the same JSON, recomputed fresh on every request, CORS-open for a dev
   server on any port. Useful once you want to try different `today` values
   (ticket expiry) or edited sample files without regenerating the static
   file by hand.

## Top level

```json
{
  "production": "Backlot Test",
  "jurisdiction": "AB",
  "today": "2026-09-05",
  "scenes": [ /* one entry per scene, see below */ ]
}
```

- `jurisdiction`: `"AB"` or `"BC"`.
- `today`: the date the run was evaluated against (`yyyy-mm-dd`), not wall-clock —
  it's a CLI argument, so re-running with a different date is how you preview
  ticket expiry moving forward.

## Per scene

```json
{
  "id": "S1",
  "heading": "INT. OFFICE - DAY",
  "day": "D1",
  "severity": "RED",
  "requirements": [ /* Requirement objects */ ],
  "locks": [ /* Lock objects */ ],
  "first_aid": { /* first aid object */ },
  "register": { "first_aider": "expired" }
}
```

- `severity`: one of `"GREEN"`, `"AMBER"`, `"RED"`, `"STOP"`, worst-first
  (`STOP` > `RED` > `AMBER` > `GREEN`). This is the single field to drive a
  gauge/badge color. Ladder (from `src/agent/locks.py:severity`):
  - `STOP` — a scene `violations` entry, or an unreleased `must_not` lock.
  - `RED` — an unreleased lock of kind `engineer`/`permit`/`competent`, or a
    `register` value of `"missing"`, `"expired"`, or `"foreign"`.
  - `AMBER` — an unreleased lock of kind `must`, or a `register` value of
    `"near_expiry"`.
  - `GREEN` — everything cleared.

### `requirements[]` — Requirement

```json
{
  "row": 9,
  "code": "AB:152",
  "part": 9,
  "section": "152",
  "heading": "Fall protection anchors",
  "text": "full section text from the OHS Code",
  "kind": "engineer"
}
```

- `row`: the hazard row (1-13) that produced this requirement; `0` means it's
  one of the always-on welfare requirements, not tied to a scene hazard tag.
- `code`: `"{jurisdiction}:{section}"`, e.g. `"AB:139"` — this is also the exact
  string format used in a scene's `violations` list.
- `kind`: `"must"`, `"must_not"`, `"engineer"`, `"permit"`, or `"competent"` —
  drives which lock role owns it (see Lock below) and the severity ladder.

### `locks[]` — Lock

```json
{
  "scene_id": "S1",
  "role": "first_ad",
  "person": "Ann Frost",
  "section_id": "7",
  "applied": "",
  "released": null
}
```

- One lock per requirement, opened automatically for every scene.
- `role`: who owns clearing it — `"engineer"`, `"safety_officer"`, `"armorer"`,
  `"rigger"`, `"first_aider"`, `"competent"` (generic fallback), or `"first_ad"`.
  A group/on-call lock (role `"on_call"`, `section_id: "GROUP"`) can appear too.
- `person`: the named individual from the plan's `roles`, or `""` if that role
  slot is unfilled (e.g. many `"competent"` welfare locks have no armorer/rigger
  attached and show `person: ""`).
- `released`: `null` while open; an ISO date string once cleared. A scene is
  clear only when every lock here has a non-null `released`.

### `first_aid` — Schedule 2 lookup (AB only)

```json
{ "table": 6, "class": "medium", "band": "close", "headcount_row": "20 – 49",
  "requirement": "1 Basic First Aider | | 1 Intermediate First Aider | | CSA Standard Z1220-17 Type 2 Basic Medium First Aid Kit" }
```

- `table`: `6` (medium hazard) or `7` (high hazard, set/strike days or any pyro
  tag). Table `5` (low hazard) is never returned — a shoot day is never low
  hazard under Schedule 2.
- `band`: `"close"` (≤20 min to hospital), `"distant"` (21-40), `"isolated"` (>40).
- For BC, this object is instead a fixed stub:
  `{"table": "3-A", "requirement": "Schedule 3-A not yet extracted", "unresolved": true}`
  — BC's Schedule 3-A hasn't been extracted yet; the front end should render
  this distinctly (e.g. "not available"), not as a normal requirement string.

### `register` — certification status by lock role

```json
{ "first_aider": "expired", "engineer": "live" }
```

- Only roles with a mapped ticket type are checked (currently `engineer` and
  `rigger` → `fall_protection`, `first_aider` → `first_aid`; see
  `agent.engine.ROLE_TICKET`). Roles not in that map (e.g. `armorer`,
  `safety_officer`, generic `competent`, `first_ad`) are omitted from this
  dict entirely — absence here does not mean "fine", it means "not tracked yet".
- Values: `"missing"`, `"foreign"`, `"expired"`, `"near_expiry"`, `"live"`
  (worst-first in that order if a role has multiple tickets).

## What the front end should NOT do

- Don't recompute severity, first-aid bands, or ticket status client-side —
  they're already resolved. Read `severity`/`first_aid`/`register` as-is.
- Don't assume a fixed requirement/lock count per scene — hazard rows that map
  to a whole OHS Code Part (`"*"` in `routing.ROUTES`) can produce well over a
  hundred requirements for one tag (e.g. BC row 9 pulls in all of Part 14,
  crane/hoist). Render as a scrollable/collapsible list, not a fixed grid.
- Don't call the OHS Code text a source of truth for anything beyond display —
  `requirements[].text` is for showing to a human, not for parsing further.
