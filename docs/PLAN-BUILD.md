# Build plan: rules engine, ADK agent, Grafana publish

Executor: any agent session in this repo. Read `CLAUDE.md`, `README.md`,
`docs/ARCHITECTURE.md`, `docs/JURISDICTIONS.md`, `docs/SETUP.md` first. Then execute
phases in order. Do not reorder. Do not add scope. Where a step says VERIFY, run the
command and use what it prints; never use a name from memory.

Conventions for every file written:
- Python 3.11+, type hints, no comments except a 1-line module docstring.
- Deterministic: no wall-clock reads inside pure functions; `today` is a parameter.
- JSON out is `json.dumps(obj, sort_keys=True, ensure_ascii=False)`.
- Every test has a negative control (an input that must fail or produce a different
  result) or it is not a test.
- Commit after each phase with the message given. Push to origin main.

Runtime environment already on disk (do not reinstall):
- venv: `.venv\Scripts\python.exe` with `mcp`, `python-dotenv`, `pypdf`.
- Grafana OSS 13.2.1 native: `.tools\grafana-13.2.1\bin\grafana.exe server`
  (start from that dir; health at http://localhost:3000/api/health).
- mcp-grafana 1.3.0: `.tools\mcp-grafana\mcp-grafana.exe`, driven by
  `src/agent/grafana_mcp.py` (modes: list | schema <tool> | call <tool> <json>).
- `.env` holds GRAFANA_URL and GRAFANA_SERVICE_ACCOUNT_TOKEN. GEMINI_API_KEY may be
  absent; Phase B checks and stops cleanly if so.
- Code data: `data/alberta-ohs/code.json` (42 parts), `data/alberta-ohs/schedules.json`
  (24 tables), `data/bc-ohs/code.json` (33 parts). Query with
  `src/agent/query_code.py <regex>`.

---------------------------------------------------------------------------------
## Phase A: deterministic rules engine (no Google dependency)

### A1 `src/agent/model.py` — data types
Dataclasses (frozen=True where noted), all JSON-serialisable via `to_dict()`:

```
Jurisdiction(province: str, municipality: str)        # province in {"AB","BC"}
Location(name, lat: float|None, lon: float|None, hospital_minutes: int|None)
Day(day: str, location: str, night: bool, exterior: bool, build_or_strike: bool,
    headcount: int, on_call: str)
Roles(first_ad, safety_officer, armorer, rigger, first_aiders: list[str], catering_lead)
SitePractice(condor_wind_kmh: float|None, crane_wind_kmh, exterior_pyro_wind_kmh,
             rig_recheck_hours: float|None, ticket_preexpiry_days: int = 90)
Plan(production, jurisdiction, locations: list[Location], schedule: list[Day],
     roles: Roles, site_practice: SitePractice, created: str, revised: str)
HazardTag(row: int, label: str, detail: str)          # row in 1..13
Scene(id: str, heading: str, day: str, tags: list[HazardTag],
      violations: list[str])   # violations: section ids the scene breaches outright,
                               # e.g. "AB:139" (work at >=3 m with no protection)
Requirement(row: int, code: str, part: int, section: str, heading: str, text: str,
            kind: str)         # kind in {"must","must_not","engineer","permit","competent"}
Ticket(person: str, role: str, issuer: str, issued: str, expires: str,
       jurisdiction: str)      # dates ISO yyyy-mm-dd
Clear(scene_id: str, section_id: str, by: str, role: str, date: str)
Lock(scene_id: str, role: str, person: str, section_id: str, applied: str,
     released: str|None)
```
`load_plan(path) -> Plan`: reads `production.plan.json`; raises `ValueError("jurisdiction required")`
if province is empty; raises `ValueError("unknown province")` if not AB/BC.

Test `tests/test_model.py`: loads `templates/production.template.json` and asserts
`ValueError("jurisdiction required")`. Negative control: a copy with province "AB"
loads.

### A2 `src/agent/routing.py` — hazard row to Code sections
Constant `ROUTES: dict[int, dict[str, list[tuple[int, list[str]]]]]` keyed by row,
then by province, listing (part, [section ids]) exactly as below. Section ids are
strings as they appear in `code.json` (`"7"`, `"139"`, `"11.2"`).

```
1  firearms:        AB: []                                  BC: []
2  pyro:            AB: [(10, ["*"]), (33, ["*"])]          BC: [(21, ["*"])]
3  chemical:        AB: [(4, ["16","17","21","22"]), (29, ["*"]), (26, ["*"])]
                    BC: [(5, ["5.53","5.97","5.98","5.101","5.104"])]
4  electrical:      AB: [(17, ["*"]), (15, ["212","213"])]  BC: [(19, ["19.10","19.16","19.18"])]
5  pressure:        AB: [(15, ["212","213","215.4"]), (25, ["*"])]
                    BC: [(12, ["*"]), (10, ["10.3"])]
6  structural:      AB: [(21, ["292.1","293","294"]), (23, ["*"]), (30, ["*"])]
                    BC: [(13, ["*"]), (15, ["*"])]
7  confined:        AB: [(5, ["47","49","52","56"])]        BC: [(9, ["9.5","9.9","9.13","9.17"])]
8  stunts:          AB: [(2, ["7","8","9"]), (9, ["139","140"])]
                    BC: [(11, ["11.2"])]
9  heights:         AB: [(9, ["139","140","152","152.1"]), (6, ["64","65","106"])]
                    BC: [(11, ["11.2"]), (14, ["*"])]
10 tools:           AB: [(25, ["*"]), (22, ["311"]), (18, ["*"])]
                    BC: [(12, ["*"])]
11 motion:          AB: [(19, ["*"]), (31, ["*"])]           BC: [(16, ["*"]), (24, ["24.63"])]
12 environment:     AB: [(7, ["115","116","117","118"]), (6, ["106"])]
                    BC: [(7, ["7.27","7.31"]), (14, ["*"])]
13 loto:            AB: [(15, ["212","213","214","214.1","215","215.1","215.2","215.4"])]
                    BC: [(10, ["10.3","10.4","10.7","10.9","10.10"]), (19, ["19.10","19.16"])]
welfare (always):   AB: [(2, ["7","8"]), (11, ["178","179","181"]), (24, ["355"]), (7, ["115","116","117"])]
                    BC: [(3, ["3.16","3.17","3.18","3.19"]), (28, ["28.10"]), (4, ["4.87"])]
```
`"*"` means every section of that part. Row 1 is intentionally empty in both
provinces: firearms thresholds are jurisdiction-supplied and not in the OHS Codes.
Row 1 still produces a Requirement of kind `"competent"` with text
"PAL holder or direct supervision by PAL holder; Actsafe MP-06-2024 (BC)" and
section id `"FIREARMS"`.

`classify(text: str) -> str`: regex on the section text, first match wins, in order:
`professional engineer` -> "engineer"; `\bpermit\b` -> "permit";
`competent (worker|person)|first aider|blaster|tending worker` -> "competent";
`must not` -> "must_not"; `must` -> "must"; else "must".

`route(scene: Scene, province: str, codes: dict[str, list]) -> list[Requirement]`:
for each tag row, and for the welfare set, resolve ROUTES against the loaded
`code.json` for that province; expand `"*"`; skip sections whose text is exactly
"Repealed."; build Requirement with kind from `classify`. Return sorted by
(row, part, section). Missing section id in code.json -> raise
`KeyError(f"{province}:{part}:{section}")` (never skip silently).

Test `tests/test_routing.py`:
- a Scene with tags [row 9] in AB returns a Requirement for section "139" kind "must"
  and one for "152" (VERIFY its kind by reading its text via query_code; assert the
  observed kind).
- negative control: same scene in BC returns no section "139" and does return "11.2".
- a Scene with no tags returns only the welfare set (AB: 11 requirements, count
  verified at run time and then pinned).
- `KeyError` when ROUTES references a section absent from code.json (inject a fake
  route in the test).

### A3 `src/agent/first_aid.py` — Schedule 2 lookup (AB only; BC returns a stub)
`hazard_class(day: Day, scene_tags: list[HazardTag]) -> str`: "high" if
`day.build_or_strike` or any tag row == 2; else "medium". (Low is never returned:
a shoot day is never low-hazard work under Schedule 2 Table 1; assert this in a test
by inspecting the Table 1 rows text for the absence of any film category.)
`travel_band(minutes: int) -> str`: <=20 "close"; 21..40 "distant"; >40 "isolated".
`headcount_band(n: int, table_rows) -> row`: match the first-column label
("1", "2 – 9", "10 – 49", "50 – 99", "100 – 199", "200 or more" for Table 5;
Table 7 uses "2 – 4","5 – 9","10 – 19","20 – 49","50 – 99","100 – 199","200 or more").
Parse the en-dash ranges; "200 or more" is >=200.
`first_aid_requirement(day, tags, hospital_minutes, schedules) -> dict`:
returns {"table": 5|6|7, "class": ..., "band": ..., "headcount_row": label,
"requirement": cell text}. AB only; for BC return
{"table": "3-A", "requirement": "Schedule 3-A not yet extracted", "unresolved": True}.

Test `tests/test_first_aid.py`: AB, 30 workers, 15 min, no pyro, shoot day ->
Table 6 (VERIFY the cell text by printing; then pin it). Negative controls:
same with `build_or_strike=True` -> Table 7; same with hospital 45 min -> band
"isolated" and a different cell text than the "close" cell.

### A4 `src/agent/register.py` — certification register
`load_register(csv_path) -> list[Ticket]`; CSV header exactly:
`person,role,issuer,issued,expires,jurisdiction`.
`VALIDITY_YEARS = {("fall_protection","AB"):3, ("fall_protection","BC"):3,
("first_aid","AB"):3, ("first_aid","BC"):3, ("mobile_equipment","AB"):3,
("mobile_equipment","BC"):3, ("blaster","BC"):5, ("pal","*"):5, ("ncso","AB"):3}`
(source: docs/JURISDICTIONS.md certifications table).
`status(ticket, today: str, preexpiry_days: int, province: str) -> str`:
- effective_expiry = min(ticket.expires, ticket.issued + VALIDITY_YEARS[(role, province)]
  or (role,"*")) when a validity is known; else ticket.expires.
- ticket.jurisdiction not in {province, "*", "federal"} -> "foreign".
- today > effective_expiry -> "expired"; today + preexpiry_days >= effective_expiry
  -> "near_expiry"; else "live".
`check_role(register, role, province, today, preexpiry_days) -> str`:
"missing" if no ticket for role; else the worst status among that role's tickets
in order missing > foreign > expired > near_expiry > live.

Test `tests/test_register.py`: a ticket issued 2022-01-01 expiring 2027-01-01 for
fall_protection AB with today 2026-09-04 -> "expired" (3-year validity governs,
shorter wins). Negative control: issued 2024-06-01 -> "live"; today 2027-05-15 with
preexpiry 90 -> "near_expiry"; jurisdiction "CA" -> "foreign".

### A5 `src/agent/locks.py` — hold, lock, verify, group
State kept in a dict `{scene_id: {"hold": bool, "locks": [Lock], "verified_by": str|None}}`.
```
open_hold(state, scene_id, requirements) -> None
   sets hold=True; creates one Lock per (role, section) for roles named by kind:
   engineer -> roles.rigger or "engineer"; permit -> roles.safety_officer;
   competent -> role by row: 1 armorer, 9 rigger, 11 first_aider... (table in code);
   must/must_not -> roles.first_ad. Person = the plan's roles mapping; "" if unset.
release(state, scene_id, role, person, section_id, date) -> None
   raises PermissionError if the lock's person != person (owner-only).
verify(state, scene_id, by: str) -> bool
   returns True and sets hold=False only if zero unreleased locks AND `by` != the
   person who released the last lock. Else False.
group_lock(state, scene_id, coordinator: str) -> None
   adds a Lock with role "on_call"; it cannot be released while any other lock is
   unreleased (raise PermissionError).
severity(state, scene_id, requirements, register_status: dict[str,str]) -> str
   "STOP" if any scene violation or any lock of kind must_not unreleased;
   "RED" if any unreleased lock of kind engineer|permit|competent, or any
         register_status value in {"missing","expired","foreign"} for a named role;
   "AMBER" if any unreleased lock of kind must, or any "near_expiry";
   "GREEN" otherwise (hold closed).
```
Test `tests/test_locks.py`: owner-only release raises for a different person
(negative control: same person succeeds); verify by the last releaser returns False,
by another returns True; group lock cannot release while a personal lock remains;
severity ladder: build a state per level and assert; negative control: releasing the
engineer lock drops RED to AMBER when a must lock remains.

### A6 `src/agent/engine.py` — one run
`run(plan: Plan, scenes: list[Scene], clears: list[Clear], register: list[Ticket],
today: str, codes, schedules) -> dict`:
for each scene: route -> requirements; apply clears (a Clear releases the matching
lock); first_aid for the scene's day; register checks for every role named by the
requirements; severity; emit
```
{"production":..., "jurisdiction":..., "today":..., "scenes":[
   {"id","heading","day","severity","requirements":[...],"locks":[...],
    "first_aid":{...},"register":{role:status}}]}
```
`replay(plan_path, scenes_path, clears_path, register_path, today) -> str`: runs
twice and returns the JSON only if the two byte strings are identical; else raises
`AssertionError("non-deterministic")`.

CLI: `python -m agent.engine samples/production.plan.json samples/scenes.json
samples/clears.json samples/crew.csv 2026-09-05` prints the JSON.

Test `tests/test_engine.py`: replay equality on the samples; negative control: a
scene with a `violations` entry yields "STOP"; removing it yields not "STOP".

### A7 samples (hand-authored, no rights issues)
- `samples/production.plan.json`: production "Backlot Test", AB, Calgary, one
  location "Warehouse 9" hospital_minutes 15, two days: D1 shoot (headcount 30,
  exterior false), D2 pyro exterior night (headcount 42, exterior true), roles filled
  with placeholder names, on_call "Dana Rigger" on D2, site_practice nulls.
- `samples/scenes.json`: three scenes. S1 interior dialogue, tags []. S2 D2
  "EXT. LOADING DOCK - NIGHT", tags [row 2 pyro "flash pot", row 9 heights
  "performer on 4 m platform", row 13 loto "hydraulic lift reset between takes"],
  violations []. S3 same as S2 plus violations ["AB:139"].
- `samples/clears.json`: one Clear releasing S2's engineer lock on section "152" by
  "Dana Rigger".
- `samples/crew.csv`: 6 rows; "Dana Rigger" fall_protection issued 2024-06-01;
  "Sam Aid" first_aid issued 2022-01-01 (expired by validity); armorer absent.

Expected after A6 on these samples with today 2026-09-05: S1 GREEN or AMBER
(welfare musts unreleased -> AMBER; pin the observed), S2 RED (first_aid expired ->
RED even after the engineer clear), S3 STOP. Pin the observed values in the test.

Phase A gate:
```
.venv\Scripts\python.exe -m pytest -q tests
```
must print `N passed, 0 failed`. Then commit:
`Rules engine: routing, first aid, register, locks, engine; samples; tests`.

---------------------------------------------------------------------------------
## Phase B: ADK agent with Gemini and the Grafana MCP toolset

### B1 install and VERIFY names
```
.venv\Scripts\python.exe -m pip install google-adk google-genai
.venv\Scripts\python.exe -c "import google.adk, google.genai; print(google.adk.__version__, google.genai.__version__)"
.venv\Scripts\python.exe -c "import pkgutil, google.adk.tools as t; print([m.name for m in pkgutil.iter_modules(t.__path__)])"
```
From the printed module list, locate the MCP toolset module (expected name contains
`mcp`). Then:
```
.venv\Scripts\python.exe -c "import google.adk.tools.mcp_tool as m; print([n for n in dir(m) if 'MCP' in n or 'Stdio' in n or 'Connection' in n])"
```
Use ONLY the class names printed. Record them in `docs/PLAN-BUILD.md` under a
"VERIFIED B1" heading with the version numbers. If the import fails, print
`help(google.adk.tools)` and find the MCP class from that; do not guess.
Add `google-adk`, `google-genai` to `pyproject.toml` dependencies.

### B2 env and model
`.env` gains `GEMINI_API_KEY=` (AI Studio) and `GEMINI_MODEL=gemini-2.5-flash`.
VERIFY the auth env var name expected by the installed google-genai:
```
.venv\Scripts\python.exe -c "import google.genai as g; import inspect; print(inspect.signature(g.Client.__init__))"
```
If `api_key` is a parameter, ADK reads `GOOGLE_API_KEY`; set `GOOGLE_API_KEY` from
`GEMINI_API_KEY` in code at startup (`os.environ.setdefault`). If `GEMINI_API_KEY`
is empty, `adk_agent.py` prints `GEMINI_API_KEY missing: online steps disabled` and
exits 2. Vertex express mode is optional; if used, document the exact env vars from
the express-mode quickstart page, quoted, not recalled.

### B3 `src/agent/steps.py` — the three language steps, schema-pinned
Three functions, each calling `google.genai` with `response_mime_type="application/json"`
and a `response_schema` built from `schemas/*.json`, temperature 0:
- `diff(locked: str, revised: str) -> dict` schema `schemas/diff.schema.json`:
  `{"scenes":[{"id","heading","change":"added|removed|modified|unchanged","summary"}]}`
- `cascade(diff: dict) -> dict` schema `schemas/cascade.schema.json`:
  `{"departments":[{"name":"props|wardrobe|locations|cast|stunts|sfx|grip|electric|catering","deltas":[{"scene_id","delta"}]}]}`
- `tag(scene_text: str) -> dict` schema `schemas/tags.schema.json`:
  `{"tags":[{"row":1..13,"label","detail"}],"violations":[]}`
Prompts are constants in `src/agent/prompts.py`, each under 12 lines, each ending
with "Output JSON only, matching the schema."
Offline queue: if the call raises a network error, append the request to
`.queue/<step>-<sha256 of input>.json` and return `{"queued": True}`. `replay_queue()`
re-runs queued items when online.

Test `tests/test_steps_offline.py`: monkeypatch the client to raise
`ConnectionError`; assert a `.queue/` file is written and the return has
`queued: True`. Negative control: monkeypatch to return a valid JSON; assert no
queue file and the parsed dict matches the schema (validate with `jsonschema`, add
to deps).

### B4 `src/agent/adk_agent.py` — the agent
Using ONLY the names verified in B1:
- MCP toolset over stdio: command `.tools\mcp-grafana\mcp-grafana.exe`, env from
  `.env` (GRAFANA_URL, GRAFANA_SERVICE_ACCOUNT_TOKEN).
- Function tools: `run_engine(plan_path, scenes_path, clears_path, crew_csv, today)`
  (wraps engine.run), `first_aid_for_day(day)`, `code_section(province, part, section)`
  (returns the section text from code.json).
- Agent name `backlot_safety`, model from `GEMINI_MODEL`, instruction under 15 lines:
  the agent must (1) call diff/cascade/tag, (2) call run_engine, (3) for each scene
  with severity RED or STOP call the MCP `create_incident` tool and for each lock
  call `create_annotation` with text `"{role} · {person} · {section_id} · {heading}"`
  and tags `["backlot", scene_id, severity]`, (4) reply with the JSON from run_engine
  and nothing else.
VERIFY the argument schemas of `create_incident` and `create_annotation` with
`grafana_mcp.py schema <tool>` before writing the calls; use only the fields printed.

Run: `.venv\Scripts\adk run src/agent` (or the CLI form printed by `adk --help`).
Input: paste `samples/revision.txt` (write it: a 40-line scene, locked vs revised,
where the revision adds a flash pot on the loading dock).

### B5 runtime receipts (write them into README "Status")
- `RUNTIME: adk run -> diff/cascade/tag JSON printed, engine JSON printed, Grafana
  incident id N created, K annotations created` (paste the ids).
- `RUNTIME: network disabled -> engine JSON identical, 3 queue files written,
  incident and annotations still created (Grafana is local)`.
- `RUNTIME: replay -> two runs byte-identical`.
Commit: `ADK agent: Gemini steps schema-pinned, engine tools, Grafana MCP toolset;
runtime receipts`.

---------------------------------------------------------------------------------
## Phase C: wall and hand-off (only after B5 receipts exist)
- Grafana dashboard JSON `grafana/backlot.dashboard.json` with four panels:
  severity per scene (annotations list), open locks (annotations filtered by tag),
  first aid requirement (text panel updated via `update_dashboard`), on-call (text).
  Import via the MCP `update_dashboard` tool; VERIFY its schema first.
- README: replace "Status" with the receipts; add "Run it" with the exact commands.
- Do not start Sehrish's web page from this plan; it consumes the engine JSON.

Out of scope for this plan: Gemma sidecar, Vertex Agent Engine deploy, BC Schedule
3-A extraction, Row 1 thresholds, any lattice organ.
