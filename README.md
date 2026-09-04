# Summer Blockbuster Hackathon — IBM Track

Agentic workflow on **Google Cloud Gemini Enterprise / Agent Builder**, integrating
**IBM watsonx Orchestrate** to solve a real media & entertainment enterprise-automation
problem.

Team: Sean, Sheresh

## Track

- **Partner:** IBM (watsonx Orchestrate)
- **Platform:** Google Cloud Gemini Enterprise Agent Platform

## Repo boundary

This repository is **net-new** for the hackathon. No code, assets, or doctrine files
are ported from any other private repository. Everything here must be safe for public
disclosure and judging by Google and IBM.

Do not commit:
- API keys, service account JSON, `.env` files
- Any internal/private project files not authored for this hackathon

## Requirements checklist (from Devpost)

- [ ] Hosted project URL
- [ ] 3-minute demo video (YouTube/Vimeo, public, English)
- [ ] Public repo with open-source license (this repo, MIT — see `LICENSE`)
- [ ] Demonstrates actual runtime use of Google Cloud + IBM watsonx (imported/called
      in code, not just named)
- [ ] Partner track selected: IBM
- [ ] Devpost submission form completed

## Structure

```
src/agent/       Agent implementation (Gemini Enterprise + watsonx Orchestrate calls)
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

## Status

Scaffold only — architecture and idea TBD.
