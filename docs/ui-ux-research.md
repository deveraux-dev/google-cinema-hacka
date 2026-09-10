# UCS UI/UX Research And Design Decisions

## Brief

UCS serves a 1st AD, safety lead, or production coordinator who needs to answer one question quickly: **can this revised scene move to the next production step, and who must act first?** The interface therefore optimizes for a fast verdict, visible evidence, and a truthful runtime receipt. It is a production cockpit, not a generic AI chat surface.

## Research Method

The review compared established production workflow products, Grafana's event model, and recurring patterns in public hackathon projects. The focus was information hierarchy, script-to-workflow continuity, operational tags, evidence, and demo clarity. Inspiration was used as a pattern source; no visual asset or copy was copied into the product.

## Repeated Product Patterns

| Pattern | What strong products do | UCS adaptation |
| --- | --- | --- |
| Script-anchored change | Breakdown tools connect script elements to production documents and keep the scene as the source of truth. | Show the revision diff first, then cascade the change into departments, clearances, hazards, and statutory basis. |
| Compact tags | Production workflows use short labels for elements, departments, and risk categories so a busy operator can scan before reading. | Scenario cards expose concise scene-signal tags such as `PYRO`, `HEIGHTS`, `FIREARMS`, and `CONFINED SPACE`. Tags support the verdict; they do not replace evidence. |
| Connected workflow | Call-sheet tools reuse current schedule/script/catalog data instead of asking users to re-enter it. | Scenario selection hydrates the editor and review request from the same backend scenario contract. |
| Event receipts | Grafana annotations attach text, tags, and links to a time-based operational view. | The frontend labels live publish, historical receipt, snapshot, and fallback separately. It never calls a snapshot a new publish. |
| One memorable outcome | Successful hackathon demos make the problem, action, and proof obvious in a short path. | `Select revision -> Analyze -> ROLL/HOLD/STOP -> clearances -> evidence -> receipt`. |
| Trust before spectacle | High-stakes tools expose provenance, constraints, and responsible authority. | AI is structured analysis; deterministic Python rules own the stage decision; safety personnel retain final authority. |

## Product References

- [Celtx production workflow](https://www.celtx.com/product/production/) shows a connected production workflow around scripts, breakdowns, schedules, call sheets, reports, and sharing.
- [Celtx breakdown guidance](https://support.celtx.com/hc/en-us/articles/360000078548-Breaking-Down-a-Script) describes extracting script elements into production information that persists through later documents.
- [StudioBinder script breakdown](https://www.studiobinder.com/script-breakdown-software/) uses categorized script elements that sync into scheduling and production documents.
- [Grafana annotations](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/annotate-visualizations/) defines annotations as rich events with text, tags, and links that can be inspected on dashboards.
- [Public hackathon-winner projects](https://github.com/topics/hackathon-winner) repeatedly foreground a focused problem, a working integration, and a demoable outcome rather than a large feature list.

## UCS Design Direction

### Hierarchy

1. **Decision:** ROLL, HOLD, or STOP, with a one-sentence reason.
2. **Action:** next move, affected teams, and required sign-offs.
3. **Evidence:** revision diff, hazard signals, statutory basis, and department cascade.
4. **Proof:** structured chain, delivery provenance, and Grafana receipt.

### Visual language

Graphite surfaces, warm high-contrast text, restrained blue for interaction, amber for review/fallback, green for clear, red for stop, and a distinct hold state. Color is paired with words, badges, and layout so safety meaning is never color-only. Typography is compact and scannable; cards frame meaningful evidence rather than decorate the page.

### Interaction and responsive rules

- One primary action: `Analyze revision`.
- Scenario cards behave like selectable controls and expose risk tags before analysis.
- Auto-review is explicit, reversible, and recorded in the runtime receipt.
- Details use progressive disclosure, but the core verdict remains visible without opening a drawer.
- Motion is limited to selection, loading, result reveal, and receipt confirmation. Reduced-motion users receive the same content immediately.
- Links look like links and only become actionable when the backend provides a valid destination.
- At 390px, 768px, 1280px, and 1440px the identity and decision hierarchy remain the same. The evidence rail stacks below the verdict on narrow screens, controls remain touch-sized, and content wraps instead of creating horizontal scrolling.

## Judge Review Priorities

### P0

- Verdict, next action, and provenance visible after one analysis.
- No false `Live Gemini` or `Grafana Published` state.
- No horizontal overflow, broken glyphs, or inaccessible controls.
- Backend JSON reaches the same DOM that the judge sees.

### P1

- Risk tags make the selected revision understandable before the request runs.
- The proof chain separates Google ADK/Gemini, deterministic safety, and Grafana roles.
- Custom revision analysis follows the same result hierarchy as scenario analysis.

### P2

- Subtle reveal motion and receipt polish.
- Additional historical navigation only when backed by a real API contract.

## Do Not Build

- A generic chatbot, a fake autonomous loop, or decorative charts with no operational meaning.
- A client-side safety verdict that can disagree with the backend.
- A public live link when only a local or historical receipt exists.
- A large feature list that makes the camera-roll decision harder to find.

## QA Checklist

- [ ] A first-time user understands the problem and primary action within 3–5 seconds.
- [ ] Selecting a scenario shows compact signals and a clear selection state.
- [ ] Analysis shows the backend result, not a fabricated loading conclusion.
- [ ] STOP/HOLD/ROLL is readable without relying on color.
- [ ] Auto-review is visible, toggleable, and represented in the receipt.
- [ ] Details, modal, tabs, links, and clearances work with keyboard input.
- [ ] 390px mobile has no horizontal overflow and preserves the verdict hierarchy.
- [ ] Snapshot, fallback, history, live request, and Grafana states are distinct.
- [ ] `pytest`, JavaScript syntax, Python compilation, diff checks, and Playwright pass.
