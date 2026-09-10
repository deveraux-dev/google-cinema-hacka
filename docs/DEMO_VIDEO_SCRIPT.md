# Universal CallSheet Hackathon Pitch Video

## Recording Target

- Duration: 2:30 to 2:45
- Format: 1920x1080 screen recording with calm voiceover
- Primary proof scenario: S2, Confined Space Prop Firearm Shootout
- Product URL: use the public Vercel URL only after deployment protection is disabled; otherwise record the verified local app at `http://127.0.0.1:8003/`
- Core story: a screenplay revision creates new physical work; UCS identifies the change, applies deterministic safety rules, and shows who must act before the camera can roll.

## Judge Story

The judge should understand these points without reading the repository:

1. A late screenplay revision can create a safety coordination gap.
2. Google ADK and Gemini convert the revision into strict structured analysis.
3. Deterministic Python rules, not the model, own the stage decision.
4. Grafana receives the post-gate receipt when its MCP connection is configured.
5. The frontend makes the decision, required action, evidence, and provenance visible.

## Shot And Narration Plan

### 0:00-0:18 - Problem And Promise

**Screen**

- Open the UCS first viewport at 1280x720 or 1440x900.
- Keep the product name, headline, scenario deck, and Analyze action visible.
- Do not scroll yet.

**Voiceover**

> A screenplay can change minutes before a take. One new line can introduce firearms, atmospheric effects, restricted egress, or stunt work before every department has updated its safety plan. Universal CallSheet turns that revision into one clear question: can the camera roll?

### 0:18-0:42 - Select The Revision

**Screen**

- Point briefly to the S2 risk tags: `FIREARMS`, `CONFINED SPACE`, and `ATMOSPHERICS`.
- Leave Auto-review on.
- Select S2 once.
- Let the automatic review run without extra clicking.

**Voiceover**

> Here, Scene S2 changes from a search in a cargo hold to a scene with heavy atmospheric smoke and blank firearm discharge inside a restricted space. With bounded Auto-review enabled, selecting the revision submits the same validated backend workflow a user can also run manually.

### 0:42-1:12 - Structured Analysis And Safety Boundary

**Screen**

- Let the four runtime stages update.
- Land on the stage decision.
- Keep `STOP`, the reason, next action, and affected teams visible.

**Voiceover**

> Google ADK and the configured Gemini model structure the revision in a fixed order: DiffOutput, CascadeOutput, then HazardTagOutput. But the model never decides whether production is safe. Those hazard tags pass into a deterministic Python rules engine. For this revision, the engine returns STOP and identifies the clearances required before rehearsal or camera roll.

### 1:12-1:42 - Show The Operational Value

**Screen**

- Open Revision impact.
- Show the removed and added screenplay text.
- Open Required clearances.
- Check one clearance to demonstrate interaction, then leave the remaining requirements visible.
- Briefly show Department cascade.

**Voiceover**

> The result is operational, not just descriptive. The 1st AD sees what changed, which departments are affected, and who must sign off. Each clearance stays visible and actionable, while the screenplay diff preserves the evidence behind the decision.

### 1:42-2:10 - Prove The Runtime Chain

**Screen**

- Open Hazard evidence and Statutory basis.
- Move to Receipt and chain.
- Open Raw JSON for two or three seconds.
- Point to the provenance badge and Grafana status.

**Voiceover**

> The proof reader shows the hazard evidence, statutory mapping, and the exact backend JSON. It also tells the truth about provenance. A live Gemini request is labeled live only when it actually completes. A snapshot or structured fallback is labeled separately. Grafana is shown as published only when the backend returns a verified MCP receipt.

### 2:10-2:30 - Grafana And Architecture

**Preferred screen when a fresh Grafana receipt exists**

- Open the Grafana receipt link.
- Show the annotation corresponding to the S2 run.

**Fallback screen when hosted Grafana is not verified**

- Keep the UCS receipt panel visible.
- Show the repository architecture diagram or the verified local Grafana screenshot in `docs/wall.png`.
- Add a small on-screen caption: `Local stdio verified / hosted Streamable HTTP supported`.

**Voiceover**

> After the safety gate, UCS can publish the result through the official Grafana MCP server. We verified that write path locally over stdio, and the production adapter supports authenticated Streamable HTTP. Hosted publishing is never claimed unless this run returns a receipt.

### 2:30-2:42 - Close

**Screen**

- Return to the STOP decision.
- End on the product name, STOP verdict, and one line: `AI structures. Rules decide. Production acts.`
- Hold the final frame for no more than two seconds after narration.

**Voiceover**

> Universal CallSheet helps a production understand what changed, stop unsafe work, and show exactly why. AI structures the revision. Deterministic rules decide. Production stays in control.

## Runtime Wording

Use the narration line that matches the visible receipt.

| Visible mode | Say this |
| --- | --- |
| `LIVE GEMINI REQUEST` | "Gemini returned the structured analysis for this request." |
| `LIVE STRUCTURED FALLBACK` | "The request used the schema-compatible fallback, clearly labeled on screen." |
| `HISTORY SNAPSHOT` or `STATIC SNAPSHOT` | "This is a previously recorded receipt, not a new model call." |
| Grafana `Published` | "The backend returned a verified Grafana MCP receipt." |
| Grafana `Skipped` | "Hosted Grafana is not configured for this run, so no publish is claimed." |

Never say `live Gemini`, `real-time Grafana`, or `published` unless the current screen proves it.

## Recording Setup

1. Restart the backend so the recording uses the current commit.
2. Open `/api/health` once and confirm `status: ok` and `json_contract: v1`.
3. Use browser zoom at 90% or 100%; hide bookmarks and unrelated tabs.
4. Set the browser viewport to 1280x720 or 1440x900.
5. Turn off notifications and hide personal account information.
6. Rehearse the S2 path twice before recording.
7. Record one clean take without cutting between the S2 click and STOP receipt.
8. Capture a separate Grafana shot only if the annotation is fresh and identifiable.

## Edit Direction

- Use direct cuts or 250-400ms crossfades.
- Keep cursor movement slow and intentional.
- Use at most two gentle zoom-ins: the STOP decision and the receipt.
- Do not use camera shake, rapid pans, repeated intros, artificial loading, or decorative sound effects.
- Keep music at least 18dB below narration, or omit it.
- Export H.264 video, AAC audio, `yuv420p`, 1920x1080, 30fps, with fast-start enabled.

## Final Judge Check

- [ ] Product and problem are clear in the first 10 seconds.
- [ ] S2 reaches STOP in one visible flow.
- [ ] The narration calls Gemini structured analysis, not the safety decision-maker.
- [ ] Deterministic safety ownership is stated plainly.
- [ ] The screen shows changed text, required action, and proof.
- [ ] Grafana wording matches the actual receipt state.
- [ ] No secrets, local usernames, browser extensions, or personal tabs appear.
- [ ] The final URL and repository URL are readable on the closing frame.
- [ ] Duration is under the event limit.
