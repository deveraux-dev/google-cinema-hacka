# Judge-ready plan

Source of truth checked on 2026-09-08: current repo files, README, team checklist,
and Devpost public pages for Agentic Cinema/Grafana.

## Verdict

The idea is strong, but the current plan is split between two histories:

- The old plan says a deterministic rules engine and Grafana publisher exist as
  `agent.engine`, `agent.publish`, and `agent.main`.
- The current checkout has an ADK revision-analysis pipeline in `core.py`,
  `models.py`, and `pipeline.py`, plus a saved ADK output fixture.

Judges will not reward the older claim unless they can run it. The plan should now
optimize for one live, judge-visible vertical slice:

1. A Gemini/ADK call turns a script revision into structured diff, cascade, and
   hazard tags.
2. A deterministic severity step converts those tags into scene status.
3. The agent writes one visible result to Grafana through the official MCP server.
4. The demo shows the same fixture still usable if Gemini/network fails.

## Official requirements

- Deadline: September 9, 2026 at 2:00pm PDT.
- Project must be a functional agent powered by Gemini and Google Cloud.
- Grafana track must actively use the Grafana stack at runtime, primarily through
  the official Grafana MCP server or hosted Grafana Cloud MCP endpoint.
- AI Observability is useful but does not satisfy the Grafana runtime requirement
  by itself.
- Submission needs a hosted project URL, public repo, public 3-minute video, and
  Devpost form.

Sources:

- https://agentic-cinema.devpost.com/
- https://agentic-cinema.devpost.com/rules
- https://agentic-cinema.devpost.com/details/grafana-resources

## Strong judge signal

The clearest win condition is not "more safety-code coverage." It is a visible,
auditable chain:

`script revision -> ADK/Gemini structured JSON -> deterministic safety decision -> Grafana MCP write -> wall changes`

The demo should make that chain undeniable in under 90 seconds.

## Priority

P0 BLOCKER: Reconcile claims with runnable code.

- Replace or clearly demote references to missing `agent.main`, `agent.publish`,
  and `agent.engine` until those files exist again.
- Treat `samples/adk_pipeline_output.json` as the verified artifact for the ADK
  path.
- Do not claim Grafana publish is verified in this checkout until the publisher or
  MCP call path is present and runnable.

P0 BLOCKER: Capture one live Gemini receipt.

- Use the current ADK pipeline.
- Run one known revision and save the resulting JSON.
- Record exact command, model, date, and output file.
- Keep the prompt contracts short and schema-bound.

P0 BLOCKER: Capture one Grafana MCP receipt.

- Prefer the smallest write that proves the track requirement: create/update a
  dashboard annotation from the analyzed scene output.
- Verify the MCP tool schema before calling it.
- Save the resulting annotation/dashboard id in README.
- If incidents are unavailable on local OSS, say annotations/dashboard only.

P1 JUDGE-CRITICAL: Add a deterministic severity bridge.

- Do not rebuild the full legal rules engine before the deadline.
- Map hazard rows to demo severity with a tiny documented table:
  row 2 pyro = RED, row 9 heights = RED, explicit violation = STOP,
  no hazard = GREEN/AMBER depending on welfare/register availability.
- Label this as "demo severity bridge" unless the full engine is restored.

P1 JUDGE-CRITICAL: Make the hosted project URL a reader, not a second product.

- Hosted page should consume `samples/adk_pipeline_output.json` or a generated
  `samples/demo_result.json`.
- Show scene severity, department deltas, hazard tags, and a Grafana link.
- Do not spend time building login, editing workflows, dashboards inside the web
  app, or extra jurisdictions.

P1 JUDGE-CRITICAL: Script the video around proof, not feature tour.

- 0:00-0:20 problem: script rewrite changes work and safety obligations.
- 0:20-0:55 paste/run revision through ADK/Gemini and show structured JSON.
- 0:55-1:30 show deterministic severity and lock/escalation result.
- 1:30-2:10 show Grafana changed through MCP.
- 2:10-2:40 show hosted URL reading the same output.
- 2:40-3:00 name offline fallback and limitations.

P2 POLISH: Improve language and visuals only after receipts exist.

- Tighten README.
- Add one architecture diagram or screenshot.
- Add limitation notes: not legal advice, AB/BC scope, demo severity if applicable.

## Defer

- BC Schedule 3-A extraction.
- Full premises layer.
- On-call schedules and incidents if local Grafana OSS does not support them.
- Extra frontend views.
- Weather unless it is already wired.
- More prompt optimization after one reliable live run exists.

## Final execution order

1. Fix docs so public claims match current files.
2. Create one demo result JSON from the current ADK pipeline.
3. Add the smallest deterministic severity bridge if no full engine exists.
4. Add the smallest Grafana MCP publisher that creates a visible annotation.
5. Update README with exact receipts.
6. Deploy the hosted reader page.
7. Record the 3-minute video.
8. Complete Devpost.

## Best move

Build only the receipt path now. A judge-visible Gemini output plus one Grafana MCP
write is worth more than a broad but unverifiable safety engine.
