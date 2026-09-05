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
