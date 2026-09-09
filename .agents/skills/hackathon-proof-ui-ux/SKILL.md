---
name: hackathon-proof-ui-ux
description: Design, review, or prompt hackathon frontend/UI/UX work as a proof-first judge surface, using the 13forge portal pattern without copying its implementation or visual skin.
---

# Hackathon Proof UI/UX

Use this skill when the user asks for frontend, UI, UX, public demo portal, hosted reader, proof dashboard, Devpost screenshots, or visual product polish for a hackathon submission.

This skill is about **judge comprehension and proof quality**, not color taste. It should help the user avoid wasting energy on decorative frontend work that does not improve the chance of winning.

## Core Standard

A strong hackathon UI lets a judge understand the product in 3-5 seconds and verify the core claim in under 60 seconds.

The frontend should answer:

- What is this product?
- What changed or was proposed?
- What did the system decide?
- Why did it decide that?
- What sponsor/tool receipt proves the path?
- What is live, recorded, tested, or fallback?

If the interface cannot answer those questions quickly, simplify the UI before adding more features.

## 13forge Reference Pattern

The 13forge proof portal pattern to preserve:

- A clear mode label such as `RECORDED PROOF`, `LIVE`, `DEMO MODE`, or `OFFLINE FALLBACK`.
- A literal headline that states the high-stakes product moment.
- A one-screen proof path: AI proposal -> deterministic checks -> external integration only if allowed.
- Small top metrics that prove the result, such as case count, gate count, and blocked external calls.
- A replay or step list showing each gate and its status.
- A refusal/approval receipt with the exact deterministic reason.
- A calculation or evidence panel explaining the result in plain language.
- A system map that separates creative AI from deterministic control.
- A claim discipline section that labels what is verified, tested, supported, recorded, or unverified.
- No credentials, live balances, private data, or invented performance claims in the public frontend.

Do not copy 13forge code, private assets, proprietary engine details, or visual identity blindly. Reuse the **information architecture and proof mechanics**.

## UI Priorities

Prioritize in this order:

1. Judge understands the product and stakes.
2. Judge sees the core input and output.
3. Judge sees deterministic decision logic separated from AI output.
4. Judge sees the sponsor/tool integration receipt or honest fallback receipt.
5. Judge can trust claim labels.
6. The page works on hosted URL, local file/server, desktop, and mobile.
7. Visual polish supports scanning and confidence.

Reject UI work that does not improve one of these priorities.

## Proof Surface Layout

For most hackathon products, use this structure:

- Header: product name, track/sponsor, mode label, GitHub/demo links.
- Opening band: one-sentence product truth and the important state/result.
- Proof stats: 3-4 small metrics that summarize the demo outcome.
- Workflow strip: input -> AI/extraction -> deterministic gate -> sponsor/tool -> output.
- Main proof panel: current case, input summary, decision badge, reason, receipt.
- Step/gate panel: ordered checks with status and owner/source.
- Evidence panel: calculation, citation, JSON snippet, log excerpt, annotation id, test name, or API receipt.
- System panel: short architecture map showing what AI controls and what code controls.
- Claim panel: what is live, recorded, tested, supported, unavailable, or intentionally excluded.

Keep the first viewport useful. Do not hide the result below a long hero or marketing copy.

## Interaction Rules

- Build one strong demo path before adding filters, tabs, settings, or alternate cases.
- Use a primary action only when it advances the proof, such as `Run safety replay`, `Check revision`, or `View receipt`.
- After action, show visible progress through steps instead of a vague spinner.
- Final state must be unmissable: `REFUSED`, `STOP`, `CLEARED`, `PUBLISHED`, or domain equivalent.
- If the demo is static or recorded, label it honestly beside the action.
- Never make a replay look live if it does not contact live services.
- Keep copy plain enough for non-technical judges, with technical receipts available nearby.

## Visual And UX Rules

- Use hierarchy before decoration: title, status, reason, receipt.
- Use color as reinforcement, not the only signal.
- Add text labels or icons for status states.
- Keep cards reserved for real repeated items or proof panels; avoid nested cards.
- Make numbers and decisions large enough to scan, but keep explanation compact.
- Prefer dense, operational layouts for production, finance, safety, logistics, and backend tools.
- Use accessible contrast, keyboard focus, and readable mobile layout.
- Avoid one-note palettes, ornamental hero sections, vague abstract imagery, and decorative dashboards.
- Text must fit in buttons, badges, tables, cards, and mobile columns without overlap.

## Backend Contract For UI

The UI should read from one canonical artifact when possible:

```json
{
  "mode": "live | recorded | fallback",
  "project": "...",
  "input": {},
  "ai_output": {},
  "deterministic_decision": {
    "status": "REFUSED | STOP | CLEARED | PUBLISHED",
    "reason": "...",
    "rule_id": "..."
  },
  "steps": [],
  "receipts": [],
  "claims": []
}
```

If this shape does not match the project, preserve the principle: one source of truth feeds UI, screenshots, README, and demo.

## Review Checklist

When reviewing a frontend, classify issues:

- `P0`: page does not load, hosted route fails, JSON fetch fails, result is false/misleading, secret appears, or claim contradicts artifact.
- `P1`: judge cannot understand the product quickly, status/reason/receipt is hidden, AI/deterministic boundary is unclear, mobile layout breaks, or sponsor proof is weak.
- `P2`: copy polish, spacing, micro-interactions, screenshot quality, motion, minor accessibility improvements.
- `SKIP`: decorative changes that do not improve proof or trust.

Always fix P0/P1 before visual flair.

## Prompting Mode

If the user must build with Gemini, Antigravity, or another allowed hackathon tool, do not directly rewrite submission code unless authorized. Provide a copy-paste prompt that tells the builder to:

- inspect current frontend files and output artifact;
- preserve clean-room provenance;
- keep the UI proof-first;
- show mode labels and receipts honestly;
- separate AI output from deterministic decisions;
- add accessible status states;
- verify desktop and mobile layout;
- report exact changed files and remaining risks.

## Output Style

For reviews, use:

`VERDICT` -> `JUDGE SEES` -> `P0/P1/P2` -> `FIX` -> `NEXT`

For build prompts, provide one direct prompt the user can paste into Gemini/Antigravity.

For implementation, keep changes scoped to the frontend/proof reader unless the user asks for backend changes.

## Winning Heuristic

The best hackathon frontend is not the prettiest page. It is the clearest proof artifact.

If a judge can say, "I understand the product, I saw the gate work, and I trust the receipt," the UI is doing its job.
