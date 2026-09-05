# Architecture

## Pipeline (fixed order, every run)

```
revised pages ──► DIFF ──► CASCADE ──► HAZARD TAG ──► WEATHER ──► ESCALATE ──► PUBLISH
                   │          │            │                          │            │
                Gemini     Gemini       Gemini                     rules       Grafana
              (or Gemma) (or Gemma)   (or Gemma)                 (NCSO ladder)  (OSS, local)
```

- DIFF, CASCADE, HAZARD TAG: language steps. Online = Gemini via Google Cloud.
  Offline = local Gemma sidecar. Same JSON schema out of both, enforced by
  structured output, so the rules never see free text.
- WEATHER: open-meteo current conditions for the shoot location. Pasquill-Gifford
  stability class computed locally. Cached, so offline mode uses the last fetch.
- ESCALATE: a lookup table, not a model call. Inputs: hazard tags, wind, stability
  class, daylight. Output: one of GREEN / AMBER / RED / STOP plus the required
  action. Authored by the team's NCSO. Every row has a negative test.
- PUBLISH: two Grafana touchpoints. Readings (per-department delta counts, wind,
  escalation level) to a data source. Escalation events to the annotations API so
  they appear as marks on every panel. Data source choice is pinned at the first
  runtime receipt, not before.

## Must show, at runtime

- A Gemini call returning the DIFF schema, logged.
- A Grafana panel changing because the agent wrote to it, on screen.
- The same run with the network disabled, using the Gemma sidecar.

## Deterministic claim

Same revision + same weather = same deltas, same escalation, byte-for-byte.
The language steps are pinned by schema and temperature 0; the rules are pure.
A replay test asserts this.

## Not in scope

- 3D location scans or blast/plume radii. The hazard tag names the exposure;
  it does not simulate it.
- Any private tooling. See README repo boundary.
