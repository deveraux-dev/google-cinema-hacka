# UCS JSON Contract

The FastAPI service returns one JSON object from `POST /api/analyze`. The browser
renders this object without recomputing severity or interpreting statutory text.

## Request

```json
{
  "scenario_id": "S1",
  "scene_id": "S1",
  "scene_heading": "EXT. LOADING DOCK - NIGHT",
  "original_text": "optional screenplay text",
  "revised_text": "optional screenplay text"
}
```

Known scenario IDs (`S1` through `S4`) use the preloaded scripts. Custom requests
must provide the two script fields. Text fields are bounded by the API to prevent
uncontrolled payloads and model cost.

## Response contract

```json
{
  "analysis": {
    "mode": "google_adk_gemini | offline_structured_fallback",
    "note": "human-readable provider status",
    "fallback_reason": "quota_exhausted | missing_credentials | provider_error | null",
    "provider_attempted": true,
    "structured_output_order": ["DiffOutput", "CascadeOutput", "HazardTagOutput"],
    "deterministic_decision_owner": "engine.safety.evaluate_safety"
  },
  "runtime": {
    "delivery": "live_request | history_snapshot | static_snapshot | embedded_snapshot",
    "api": "fastapi | none",
    "json_contract": "v1"
  },
  "scene": { "id": "S1", "heading": "...", "original_script": "...", "revised_script": "..." },
  "diff": [{ "scene_id": "S1", "element": "action", "old_text": "...", "new_text": "..." }],
  "department_deltas": [{ "department": "SPFX", "impact": "..." }],
  "hazard_tags": [{ "row": 2, "label": "pyro", "detail": "..." }],
  "safety": {
    "severity": "GREEN | REVIEW | RED | STOP",
    "reason": "...",
    "required_clears": ["..."],
    "statutory_citations": [{ "citation": "...", "title": "...", "statute_text": "..." }]
  },
  "grafana": {
    "published": true,
    "annotation_id": "31",
    "transport": "stdio | streamable_http",
    "dashboard_url": "...",
    "receipt": "...",
    "error": null
  }
}
```

`DiffOutput`, `CascadeOutput`, and `HazardTagOutput` are structured AI outputs
validated by Pydantic and Google ADK. They are model-generated, not deterministic.
The pure Python safety engine consumes hazard rows and owns the final severity.
Grafana publishing is optional and never changes the safety decision.

## Runtime modes

- `google_adk_gemini`: live Google ADK/Gemini returned schema-compatible output.
- `offline_structured_fallback`: credentials, quota, network, or provider execution
  was unavailable; conservative local extraction kept the safety path usable.
- `history_snapshot`, `static_snapshot`, and `embedded_snapshot`: the browser is
  showing cached/demo data, not claiming a fresh Gemini or Grafana operation.

## Endpoints

- `GET /api/health` reports non-secret provider and transport configuration.
- `GET /api/context` returns the production context.
- `GET /api/scenarios` returns the demo scenario deck.
- `POST /api/analyze` executes the complete request pipeline.
- `GET /api/latest` returns best-effort history or a marked static snapshot.
