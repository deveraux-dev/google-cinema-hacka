# Judge-ready plan

Source of truth: current repository files, tests, live deployment, demo video, and
the status labels in `README.md`.

## Verdict

The submission is strongest when it stays on one judge-visible vertical slice:

`script revision -> structured analysis -> deterministic safety decision -> Grafana receipt -> proof HUD`

The S2 scenario is the primary proof because it gives the clearest consequence:
a confined-space firearm revision reaches `STOP`, shows required clearances, and
keeps that verdict authoritative in the frontend.

## Judge-critical path

1. Open the [live app](https://universal-callsheet.vercel.app).
2. Keep `Auto-review` enabled and select S2.
3. Inspect the `STOP` verdict, clearances, evidence panels, and raw JSON.
4. Check `Receipt and chain` for analysis mode and Grafana state.
5. Use the [demo video](https://youtu.be/XzUXE0kLOAs) for the narrated version.

## Evidence map

| Judge question | Proof |
| --- | --- |
| What problem is solved? | README product story and S2 revision |
| Is the result concrete? | `STOP`, affected teams, and required clearances |
| Is the AI boundary meaningful? | ADK/Gemini extraction is separate from `engine.safety.evaluate_safety` |
| Is the partner technology real? | `src/engine/grafana_client.py` and the labeled receipt state |
| Can the claim be checked? | Raw JSON, tests, architecture doc, and evidence status table |

## Claim rules

- Say `live Gemini` only when the current response says the provider completed.
- Say `fallback` when the local schema-compatible path produced the response.
- Say `published` only when the backend returns a Grafana MCP receipt.
- Treat the public repository as pending until the owner changes GitHub visibility.
- Keep safety language assistive and jurisdiction-scoped; do not present the app as legal advice.

## Build status

- `BUILD NOW`: keep the S2 path stable, maintain the README/code-flow diagrams, and keep tests green.
- `BUILD IF TIME`: capture a fresh hosted Grafana receipt if the endpoint is available.
- `DEFER`: extra jurisdictions, auth, dashboards, mobile push, and environmental automation.
- `REJECT`: claims or features that are not backed by a current runtime receipt.

## Final check

Before submission, verify the live URL, demo URL, repository visibility, current
README links, and the exact status shown for Gemini and Grafana. The browser suite
must continue to prove that a `STOP` verdict cannot be overridden by checking
clearances.
