# Architecture

## Pipeline (fixed order, every run)

```
JURISDICTION ──► revised pages ──► DIFF ──► CASCADE ──► HAZARD TAG ──► WEATHER ──► ESCALATE ──► PUBLISH
     │                               │          │            │                          │            │
  user picks                      Gemini     Gemini       Gemini                     rules       Grafana
  loads thresholds              (or Gemma) (or Gemma)   (or Gemma)                 (NCSO ladder)  (OSS, local)
```

- JURISDICTION: first input, no default. Selects the threshold table for every hazard
  row (Alberta OHS Code, WorkSafeBC, Cal/OSHA + SB 132, …). The harmonized core never
  changes; only the numbers and the mandatory-role rules do. A row with no threshold
  for the chosen jurisdiction refuses to run rather than borrowing another's.
- STEP LADDER rows (stunts, pyrotechnics): escalation is monotonic per rung. Rung n+1
  cannot open until rung n has a recorded clear. A change to the scene resets to the
  rung the change touched.

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
