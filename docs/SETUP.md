# Production setup: seven questions, then the plan writes itself

A production manager sets this up once, in under ten minutes, from documents they
already have. Every question names the document that answers it. Nothing is typed
twice. Everything not asked is derived from the Code for the chosen jurisdiction.

| # | Question | Answered by | What it unlocks |
|---|---|---|---|
| 1 | Where is the shoot? Province and municipality. | the permit | jurisdiction tables, premises layer, permit conditions |
| 2 | Which locations? | the location list | hospital travel time per location (Schedule 2 column), weather point, occupancy layer |
| 3 | Who is on the crew? | the crew list CSV | headcount per day, certification register (tickets, expiry) |
| 4 | What are we shooting? | the script or breakdown | hazard rows auto-tagged per scene; nothing to pick from a menu |
| 5 | When? | the schedule | day or night, exterior, set build and strike days (high hazard by Schedule 2 Table 3), turnaround checks |
| 6 | Who holds which role? | the crew list, six names | 1st AD, safety officer, armorer, rigger, first aiders, catering lead: the lock owners |
| 7 | Who is on call? | one name per day | the group-lock holder; paged on RED or STOP |

Not asked, because the Code answers it:
- first aid attendants and kits per day: Schedule 2 Tables 5 to 7 from headcount,
  hazard class, and travel time
- which Parts apply per scene: from the hazard tags
- what each lock requires to clear: the section text
- the hazard assessment report skeleton with its date (s.7(2), 7(3))
- the emergency response plan skeleton (s.116 contents)
- ticket validity and pre-expiry windows: the jurisdiction tables

Output: `production.plan.json` (template in `templates/`). The agent loads it on every
run. The plan is the production's hazard assessment under Part 2, revised
automatically on every rewrite, dated per s.7(3).

Cognitive load rules for the setup itself:
- one question per screen, one document named per question
- upload the document, or type the one field, never both
- a question with a sensible default shows the default and a single "keep" action
- no question the Code can answer
- the last screen is the first wall: nothing on hold yet, quiet, dated
