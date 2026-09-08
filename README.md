# Agentic Cinema Hackathon — Grafana Labs Track

A multi-step agent on **Google Cloud Gemini** that turns one script revision into
structured per-department work deltas and hazard tags, then routes verified rule
outputs to a self-hosted **Grafana** wall through the official MCP server.

Team: Sean Morin, Sehrish 

## Track

- **Partner:** Grafana Labs (Grafana OSS self-hosted, driven through the official `grafana/mcp-grafana` MCP server)
- **Platform:** Google Cloud Gemini (Vertex AI Express Mode / AI Studio) + Agent Development Kit

## The problem

Ninety-five percent of produced films take three or more rewrites before principal
photography. A revision lands as colored pages, distributed by hand through the script
supervisor. Nothing cascades automatically to props, wardrobe, locations, stunts, or
the safety officer. The documented symptoms are actors reading the wrong line and
assistants photocopying at 3am.

The safety half is worse. On *Deadpool 2* in Vancouver, a stunt was added with no
risk assessment, no stunt safety checklist, and no perimeter. A rider died and
WorkSafeBC fined the production. On *Fast & Furious 9*, the stunt changed after
rehearsal and the matting did not move with it. The pattern across a decade of set
deaths is the same: the work changed, the hazard assessment did not. Alberta's OHS
Code says it in one clause (s.7(4)(c)): the hazard assessment must be repeated
"when a work process or operation changes." Nobody on a set has a tool that does that.

## What the agent does

0. **Jurisdiction** — the user picks where the shoot is before anything runs. Every
   threshold below is loaded from that choice. The core is harmonized; the numbers are
   local. Onus on the user to adopt their own rules. Shipping: Alberta (NCSO-authored)
   and British Columbia (WorkSafeBC regulation text, regulator-sourced). Every table
   states its own provenance.
1. **Diff** — the revised pages against the locked script, per scene.
2. **Cascade** — typed deltas per department (props, wardrobe, locations, cast, stunts).
3. **Hazard tag** — flags anything the rewrite introduced, by hazard row: stunts,
   pyrotechnics, working at heights, power tools, electrical, pressure, chemical,
   confined space, vehicles, water, firearms, exterior exposure.
4. **Weather** — current wind and cloud for the shoot location, Pasquill-Gifford
   stability class, lightning distance.
5. **Escalate** — fixed rules from GREEN to STOP. When Sean's final NCSO rules land,
   they become the deterministic safety engine. The model never decides the level;
   the rules do.
6. **Publish** — route deltas and escalations to Grafana through the official
   `grafana/mcp-grafana` MCP server via Google ADK's `McpToolset`.

Gemini does the structured AI analysis in steps 1 to 3:
`DiffOutput -> CascadeOutput -> HazardTagOutput`. These are schema-constrained model
outputs, not deterministic rules. Steps 0 and 4 to 6 are intended to be deterministic
once the NCSO safety table is finalized and wired.

## Repo boundary

This repository is **net-new** for the hackathon. No code, assets, or doctrine files
are ported from any private repository. Everything here must be safe for public
disclosure and judging by Google and Grafana Labs.

Do not commit:
- API keys, service account JSON, `.env` files
- Any internal/private project files not authored for this hackathon

## Requirements checklist (from Devpost)

- [ ] Hosted project URL
- [ ] 3-minute demo video (YouTube/Vimeo, public, English)
- [ ] Public repo with open-source license (this repo, MIT — see `LICENSE`)
- [ ] Demonstrates actual runtime use of Google Cloud + Grafana (imported/called
      in code, not just named)
- [ ] Partner track selected: Grafana Labs
- [ ] Devpost submission form completed

## Structure

```
src/agent/       Agent implementation (Gemini calls, rules, Grafana publish)
docs/            Architecture + submission notes
.env.example     Required environment variables (no real secrets)
```

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -e .
copy .env.example .env   # fill in real credentials locally only
```

If `pip install -e .` is unavailable (offline), set `PYTHONPATH=src` before any
`python -m agent.<module>` command instead.

Grafana can run as a plain native binary or as whatever local setup the demo machine
already has. The integration point in this repo is the official Grafana MCP server.

- Grafana OSS 13.2.1, standalone Windows archive: https://grafana.com/grafana/download?platform=windows&edition=oss
- Grafana MCP server: https://github.com/grafana/mcp-grafana

Default MCP launch uses `uvx mcp-grafana`, matching Grafana's quick-start path. To
use a downloaded native binary instead, set:

```
GRAFANA_MCP_COMMAND=mcp-grafana.exe
GRAFANA_MCP_ARGS=-t stdio
```

Then point the server at `GRAFANA_URL` with a service-account token or supported
username/password credentials.

## Rules that bind this repo

- Deadline: Sep 9, 2026, 2:00pm PDT.
- Project must be newly created during the contest period. Open-source
  components allowed under an OSI license, disclosed here.
- Grafana track: use the stack at runtime primarily through the Grafana MCP server.

## Status

| Half | State | Receipt |
|---|---|---|
| Structured AI analysis | verified at prior checkpoint | ADK + Gemini pipeline pushed at `d61f29d5d77de07d0b641bc7196b4d4e258c9dfd`; output order is `DiffOutput -> CascadeOutput -> HazardTagOutput` |
| Deterministic safety engine | pending final NCSO rules | no runtime claim yet |
| Grafana MCP adapter | config verified | `python -m pytest -q` -> 5 passed, 1 skipped; `python -m agent.grafana_mcp --check-config` prints sanitized `uvx mcp-grafana` config |
| Live Grafana publish | pending local Grafana + MCP credentials | no dashboard or annotation runtime claim yet |

Check the MCP config without starting Grafana:

```
$env:PYTHONPATH='src'
python -m agent.grafana_mcp --check-config
```

Live publish instructions will be added only after they pass against a running
Grafana instance through `mcp-grafana`.
