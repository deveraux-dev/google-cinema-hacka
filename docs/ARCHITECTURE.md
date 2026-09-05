# Architecture

## Pipeline (fixed order, every run)

```
JURISDICTION ──► revised pages ──► DIFF ──► CASCADE ──► HAZARD TAG ──► WEATHER ──► ESCALATE ──► PUBLISH
     │                               │          │            │                          │            │
  user picks                      Gemini     Gemini       Gemini                     rules       Grafana
  loads thresholds              (or Gemma) (or Gemma)   (or Gemma)                 (NCSO ladder)  (OSS, local)
```

- JURISDICTION: first input, no default. Selects the threshold table for every hazard
  row. The harmonized core never changes; only the numbers and the mandatory-role
  rules do. A row with no threshold for the chosen jurisdiction refuses to run rather
  than borrowing another's.
  Shipping in the demo: **Alberta** (thresholds authored by the team's NCSO from the
  Alberta OHS Code) and **British Columbia** (thresholds taken from WorkSafeBC's
  published OHS Regulation text; regulator-sourced, not practitioner-verified). Each
  table carries a `provenance` field that says which. California is a stub that
  refuses to run until someone who works under Cal/OSHA fills it.
  The pick is province + municipality, because the premises layer is enforced
  locally and Vancouver runs its own fire and building by-laws.
- TWO CODE LAYERS per jurisdiction:
    · Worker layer: OHS (Alberta OHS Code; WorkSafeBC OHSR). Routed from `data/*/code.json`.
    · Premises layer: fire code, building code occupancy, electrical code, pressure
      equipment, municipal film and pyro permits. Enforced by fire departments,
      building officials, ABSA / Technical Safety BC, and the city film office.
      Each has its own shutdown authority independent of OHS. A scene that changes
      location, adds open flame, adds a generator, or adds crowd changes the premises
      layer's answer even when the OHS answer is unchanged.
  Rows 2 (pyro), 3 (chemical), 4 (electrical), 5 (pressure), 6 (structural), and 12
  (environment) route to both layers.
- ROW 13, HAZARDOUS ENERGY CONTROL (LOTO): fires on any scene or day that services,
  resets, or strikes powered equipment: generators, distro, hydraulic gimbals, motion
  bases, air rams, cranes, LED walls, practical rigs. The Code's sequence is the
  ladder: isolate (AB s.212 / BC s.10.3), verify (AB s.213), personal lock per worker
  (AB s.214, 214.1 / BC s.10.7), group procedure where many workers or devices
  (AB s.215 / BC s.10.9). Each step needs a recorded clear before the next opens. A
  rig that is re-energized for a take and then re-entered for adjustment starts the
  sequence again; that re-entry is the change 7(4)(c) names.
- ESCALATION MIRRORS LOCKOUT. The same four rules govern every escalation and every
  on-call, not just Row 13:
    · Isolate: a hazard tag puts a HOLD on the scene. The hold is the energy-isolating
      device. Nothing on that scene proceeds while a hold exists.
    · Personal lock: each role the Code names for that hazard (armorer, rigger,
      engineer, first aider, 1st AD, safety officer) attaches its own lock to the hold,
      identified to the person. A lock is removed only by the person who applied it,
      with a dated record. No one clears another's lock. No blanket clear.
    · Verify: the scene reopens only when zero locks remain and the verify step is
      recorded by a role different from the last lock removed. Two people, never one.
    · Group control: when the roles or devices are many (crowd day, multi-rig set),
      a group lock is held by one named coordinator whose lock cannot come off until
      every individual lock is off. That coordinator is the on-call.
  In Grafana terms: HOLD = incident opened; each lock = an annotation carrying the
  role and person; verify = incident resolved by a different user than the last lock
  owner; on-call = the Grafana on-call schedule for the production, paged on any
  RED or STOP. All of it through the MCP server's incident, annotation, and on-call
  tools. The wall shows the locks, not just the colour.
- WELFARE ROWS, headcount-driven: first aid by headcount and hospital distance,
  drinking water, emergency response plan and contacts, food safety, rest turnaround.
  Inputs: crew count per day and location from the call sheet; hospital distance from
  the location. Quoted sections and turnaround numbers in docs/JURISDICTIONS.md. A
  revision that adds extras, moves location, or extends the day re-runs these rows
  even when no hazard row changed.
- STEP LADDER rows (stunts, pyrotechnics): escalation is monotonic per rung. Rung n+1
  cannot open until rung n has a recorded clear. A change to the scene resets to the
  rung the change touched.
- CERTIFICATION REGISTER: second input beside jurisdiction. Per worker, per ticket:
  issuer, ticket type, issue date, expiry date, jurisdiction of issue, retraining
  interval. Loaded from a CSV the production owns; never inferred by the model.
  The Code mandates competence or certification in 186 sections (Part 6 cranes 16,
  Part 9 fall protection 14, Part 23 scaffolds 11, Part 19 mobile equipment 11,
  Part 33 explosives 7, Part 5 confined spaces 7). When a tagged hazard routes to a
  section that names a competent worker, professional engineer, blaster, or operator,
  the register is checked for a live ticket in that role, for this jurisdiction.
  Rules, err on more retraining rather than less:
    · no ticket on record for a mandated role → RED
    · ticket expired, or issued under a jurisdiction that does not recognise it here → RED;
      STOP where the role is professional engineer, blaster, or confined-space tester
    · ticket inside the pre-expiry window (default 90 days, jurisdiction may shorten) → AMBER
    · where two jurisdictions or two ticket bodies give different validity periods,
      the SHORTER one governs
    · retraining logged after expiry does not clear the scene retroactively; the
      clear is dated from the retraining record
  Validity periods live in the jurisdiction tables (docs/JURISDICTIONS.md) with their
  source; a ticket type with no sourced period is treated as expired until one lands.

- DIFF, CASCADE, HAZARD TAG: language steps. Online = Gemini via Google Cloud.
  Offline = local Gemma sidecar. Same JSON schema out of both, enforced by
  structured output, so the rules never see free text.
- WEATHER: open-meteo current conditions for the shoot location. Pasquill-Gifford
  stability class computed locally. Cached, so offline mode uses the last fetch.
- ESCALATE: a lookup table, not a model call. Inputs: hazard tags, wind, stability
  class, daylight. Output: one of GREEN / AMBER / RED / STOP plus the required
  action. Authored by the team's NCSO. Every row has a negative test.
- PUBLISH: through the official `grafana/mcp-grafana` MCP server, per the track
  rules ("primarily through the Grafana MCP server"). The agent calls its tools to
  write readings (per-department delta counts, wind, escalation level), create
  annotations for escalation events, and raise an alert on RED/STOP. Backing data
  source is pinned at the first runtime receipt, not before.

## Surface doctrine: cognitive load of the production manager

The user is a UPM, 1st AD, or production manager, on a phone, between setups. The
surface is judged on whether it lowers their load, not on how much it shows.

- One thread. The screen answers three questions and nothing else: what is on hold,
  whose lock is on it, what takes the lock off. Code text, section numbers, and
  sources are one tap deeper, never on the first surface.
- Bridge every switch. Moving from the wall to a lock to the Code section keeps the
  scene name and the hold visible. No screen where the user has to remember where
  they came from.
- Exit belongs to the reader. Every lock is removed by its owner with one action.
  The system never auto-clears and never asks a question it can answer from the
  call sheet, the register, or the Code.
- Ration the red. A red field means STOP and only STOP. AMBER is text, not colour
  flood. If everything glows, nothing does.
- No prose on the wall. A lock reads "Rigger · Dana · anchor re-verify · s.152".
  Not a paragraph.
- Silence is authored. Nothing on hold reads as a quiet wall, not a green wall.

Sean's UI/UX research feeds this section; pointers to be added as they land.

## Must show, at runtime

- A Gemini call returning the DIFF schema, logged.
- A Grafana panel changing because the agent wrote to it via mcp-grafana, on screen.
- The same run with the network disabled, using the Gemma sidecar.

## Deterministic claim

Same revision + same weather = same deltas, same escalation, byte-for-byte.
The language steps are pinned by schema and temperature 0; the rules are pure.
A replay test asserts this.

## Not in scope

- 3D location scans or blast/plume radii. The hazard tag names the exposure;
  it does not simulate it.
- Any private tooling. See README repo boundary.
