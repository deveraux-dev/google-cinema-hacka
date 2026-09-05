# Agentic Cinema Hackathon — Grafana Labs Track

A deterministic, multi-step agent on **Google Cloud Gemini** that turns one script
revision into per-department work deltas and a safety escalation, and lights them up
on a self-hosted **Grafana** gauge wall. It keeps working with no internet.

Team: Sean Morin, Sheresh

## Track

- **Partner:** Grafana Labs (Grafana OSS self-hosted, driven through the official `grafana/mcp-grafana` MCP server)
- **Platform:** Google Cloud Gemini (Vertex AI Express Mode / AI Studio) + Agent Development Kit

## The problem

Ninety-five percent of produced films take three or more rewrites before principal
photography. A revision lands as colored pages, distributed by hand through the script
supervisor. Nothing cascades automatically to props, wardrobe, locations, stunts, or
the safety officer. The documented symptoms are actors reading the wrong line and
assistants photocopying at 3am.

The safety half is worse. On *Rust*, two prior misfires were never escalated. On
*Midnight Rider*, a railroad denied permission twice and no safety plan existed.
Both ended in a death, a fine, and a criminal sentence. Weather hits roughly half
of all outdoor shoots. The escalation path lives in people's heads.

## What the agent does

1. **Diff** — the revised pages against the locked script, per scene.
2. **Cascade** — typed deltas per department (props, wardrobe, locations, cast, stunts).
3. **Hazard tag** — flags anything the rewrite introduced: pyrotechnics, weapons,
   stunts, water, height, exterior exposure.
4. **Weather** — current wind and cloud for the shoot location, Pasquill-Gifford
   stability class.
5. **Escalate** — a fixed ladder from GREEN to STOP, authored by a certified
   National Construction Safety Officer (NCSO) on the team. Deterministic. The
   model never decides the level; the rules do.
6. **Publish** — every delta and every escalation becomes a Grafana reading and an
   annotation. The wall is what the crew reads.

Gemini does the language work in steps 1 to 3. Steps 4 to 6 are rules. When the
network is gone, a local Gemma model takes over steps 1 to 3 and the wall keeps
updating. The show goes on.

## Repo boundary

This repository is **net-new** for the hackathon. No code, assets, or doctrine files
are ported from any private repository. Everything here must be safe for public
disclosure and judging by Google and Grafana Labs.

Disclosed pre-existing dependency: the offline Gemma sidecar published for a prior
Google competition (link added when wired). It is used as-is and not claimed as new work.

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

Grafana and its MCP server run as plain native binaries. No Docker, no container runtime.

- Grafana OSS 13.2.1, standalone Windows archive: https://grafana.com/grafana/download?platform=windows&edition=oss
- Grafana MCP server v1.3.0, `mcp-grafana_Windows_x86_64.zip`: https://github.com/grafana/mcp-grafana/releases/tag/v1.3.0

Unpack both, start `grafana-server.exe`, then point `mcp-grafana.exe` at `GRAFANA_URL` with a service-account token.

## Rules that bind this repo

- Deadline: Sep 9, 2026, 2:00pm PDT.
- Project must be newly created during the contest period. Open-source
  components allowed under an OSI license, disclosed here.
- Grafana track: use the stack at runtime primarily through the Grafana MCP server.

## Status

Scaffold. Track and workflow chosen. No runtime receipt yet.
