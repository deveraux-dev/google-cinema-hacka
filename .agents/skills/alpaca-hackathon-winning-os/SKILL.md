---
name: alpaca-hackathon-winning-os
description: Recall and apply the AlpacaCOMP/13forge hackathon facts, judge-winning patterns, compliance boundaries, UI/UX priorities, backend proof checks, and submission strategy without reusing old implementation code.
---

# Alpaca Hackathon Winning OS

Use this skill when the user asks to recall Alpaca hackathon facts, transfer the 13forge winning pattern into a new hackathon, review a project from a judge perspective, prepare README/Devpost/demo materials, or harden UI/backend/agent workflows using the AlpacaCOMP lessons.

## Prime Directive

Preserve the proven pattern, not the old implementation:

**AI may propose an action; deterministic gates decide whether it may reach the sponsor integration.**

For 13forge, the action was an options trade and Alpaca was last in the path. The strongest proof was an oversized iron-condor refusal: `$2,525` possible loss exceeded the `$2,000` account safety limit, so broker submission was not reached.

When applying this skill to a new hackathon, translate the pattern to the current domain:

- `AI extraction/proposal` handles fuzzy language, documents, scripts, or intent.
- `Deterministic rule layer` makes safety, compliance, finance, routing, or escalation decisions.
- `Sponsor integration` receives only cleared outputs and returns visible receipts.
- `Judge-facing surface` shows input, reasoning summary, gate result, external receipt, and limitation labels in one understandable flow.

## Non-Negotiable Boundaries

- Do not reuse or copy private AlpacaCOMP/13forge implementation, engine code, credentials, private receipts, or proprietary assets into a new submission.
- Do not claim "live", "verified", "real-time", "production", "safe", or "guaranteed" unless current repo evidence proves that exact claim.
- Do not fabricate hackathon rules, judging criteria, sponsor requirements, metrics, balances, fills, test counts, or benchmark numbers.
- If current rules or sponsor requirements matter, verify official/current sources before making a compliance claim.
- If the user says only Google/Gemini tools are allowed for a submission, do not modify submitted product code with non-allowed tooling. Provide a prompt/spec for the allowed builder instead.
- Keep secrets out of commits, frontends, logs, demo screenshots, and generated artifacts.
- Treat dirty or untracked repo files as user work unless the user explicitly asks to change them.

## Judge Lens

For any review, answer the question: **what would stop a strong judge from choosing this?**

Prioritize:

- `P0 BLOCKER`: breaks the demo, rules, deployment, core behavior, or claim integrity.
- `P1 JUDGE-CRITICAL`: weakens understanding, sponsor proof, differentiation, or trust.
- `P2 POLISH`: improves perceived quality after P0/P1 are handled.
- `SKIP`: does not improve the core proof before deadline.

Strong judge signals:

- One clear problem with real stakes.
- One short workflow that proves the product works.
- A visible deterministic decision boundary.
- Sponsor technology shown in the live path or honest recorded path.
- Receipts: JSON output, annotation id, broker refusal, logs, tests, screenshots, or hosted URL.
- README, demo video, UI, and Devpost tell the same story.
- Limitations are honest and framed as engineering judgment.

Weak judge signals:

- Feature tour instead of proof.
- Decorative dashboard with unclear source of truth.
- LLM making strict safety/finance/compliance decisions.
- Sponsor tool bolted on at the end with no product reason.
- Static replay presented as live.
- Claims that are bigger than the code.

## Product Pattern From Alpaca

13forge judge-facing truth:

- It is not a trading chatbot.
- It is not "AI sends orders to Alpaca."
- It is: **AI can suggest a trade, 13forge checks it before money moves, and Alpaca is last.**

Transferable lines:

- "A judge can see the idea, the checks, and the result in one screen."
- "The external integration is placed at the end of the path, not the beginning."
- "The demo succeeds by refusing the unsafe action."

For a new project, create the equivalent sentence:

`AI can <propose/extract/detect> X; deterministic code checks Y; only cleared outputs reach <sponsor/tool>; the demo proves this with Z receipt.`

## Backend And Agentic Workflow Rules

- Use LLMs for interpretation, extraction, summarization, and structured output.
- Use deterministic code for thresholds, gates, money, safety, law, compliance, ordering, and escalation.
- Put the sponsor integration after validation, never before it.
- Make every external call return a receipt that appears in the final artifact.
- Create a single canonical JSON result that the UI, README screenshots, and demo can all reference.
- Add regression tests for the refusal/block path first; a blocked dangerous action is often the strongest demo.
- If an API is unavailable, produce an honest fallback artifact with `mode`, `source`, `timestamp`, and `not_live` style labels.
- Do not add a database, auth system, chat layer, or complex dashboard unless it directly strengthens the proof path.

## UI/UX Winning Factors

The first screen must answer in 3-5 seconds:

- What is this product?
- What input changed?
- What decision did the system make?
- Why did it make that decision?
- What external receipt proves it?

Design the UI as a proof surface, not a landing page:

- Show one workflow from left to right or top to bottom.
- Use a strong status badge for `ALLOWED`, `BLOCKED`, `STOP`, or equivalent.
- Show the deterministic reason beside the result.
- Show source evidence and sponsor receipt near the decision.
- Use plain language labels before technical labels.
- Make warning states accessible beyond color: text, icon, border, and summary.
- Keep mobile and desktop hierarchy consistent.
- Avoid decorative complexity, hidden navigation, vague metrics, or screenshots that do not prove the claim.

## README And Devpost Checklist

Make public docs match code evidence:

- `What it does`: one-sentence product truth and proof path.
- `Why it matters`: real user pain and risk.
- `How it works`: LLM step, deterministic gate, sponsor integration, reader output.
- `Built with`: only tools actually used.
- `How to run`: exact commands and required environment variables.
- `Proof/receipts`: output JSON, hosted URL, screenshot, test result, annotation id, broker result, or equivalent.
- `Limitations`: offline/static/demo-mode labels, unsupported jurisdictions, missing live credentials, or current known gaps.
- `Compliance`: state what is net-new, what is external dependency, what is excluded, and what is not claimed.

Never let README say "all verified" while the current artifact says a sponsor publish failed or credentials were missing.

## Demo Script Spine

Prefer a 2-3 minute judge demo:

- `0:00`: Problem in one sentence.
- `0:20`: Show the changed input.
- `0:45`: Show the AI extraction/proposal.
- `1:10`: Show deterministic gate and explain that the model does not decide the hard rule.
- `1:40`: Show sponsor integration receipt or honest fallback receipt.
- `2:10`: Show the one-screen proof reader.
- `2:40`: Close with why this matters and what is real today.

The demo should prove one important behavior, not tour every feature.

## Output Style

When using this skill for review, keep the response compact:

`VERDICT` -> `JUDGE SEES` -> `STRONG` -> `PROBLEM` -> `PRIORITY` -> `FIX` -> `NEXT`

When creating a prompt for Gemini/Antigravity, produce a copy-paste prompt that:

- states the clean-room/provenance boundary;
- names the exact files to inspect;
- asks for evidence before claims;
- prioritizes P0/P1 fixes;
- preserves the deterministic gate architecture;
- forbids unsupported live/safety/profit claims;
- asks for a final receipt checklist.

## Best Move Heuristic

If the user is overbuilding, redirect to the shortest proof path:

`input fixture -> model extraction -> deterministic gate -> sponsor receipt/output JSON -> one-screen UI -> README/Devpost proof`

Winning comes from making the judge trust the path quickly, not from adding more surface area.
