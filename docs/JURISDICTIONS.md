# Jurisdiction tables: Alberta and British Columbia

Harmonized rows, local numbers. Every number below is quoted from the regulator's
published text with its section where the fetch returned one. Blank means "not fetched
in the sources reached", never "does not exist".

Provenance:
- **Alberta**: Alberta OHS Code, Alta Reg 191/2021, via search-ohs-laws.alberta.ca.
  Thresholds in the ladder are authored by the team's NCSO (works under this Code).
- **British Columbia**: WorkSafeBC OHS Regulation, BC Reg 296/97, bclaws consolidation
  last amended April 1, 2026, in `data/bc-ohs/` under the King's Printer Licence – BC,
  plus Actsafe BC motion-picture bulletins. Regulator-sourced, not practitioner-verified.
- **Ticket periods**: where the only source is a training vendor's page, the row says
  "(vendor)". Vendor-sourced periods are treated as the ceiling; the agent uses the
  shorter of vendor period and any regulator period.

## The duty that makes the cascade a legal obligation

| | Alberta | BC |
|---|---|---|
| Reassess on change | Part 2 s.7(4), King's Printer text: repeated "(a) at reasonably practicable intervals …, (b) when a new work process is introduced, (c) when a work process or operation changes, or (d) before the construction of significant additions or alterations to a work site." Confirmed from the consolidation in `data/alberta-ohs/`. | Part 5 s.5.53(1) (chemical): reassessment "when there is a change in work conditions which may increase the exposure, such as a change in production rate, process or equipment." A general Part 3/4 duty exists but was not fetched. |
| Worker involvement | Part 2 s.8(1): "An employer must involve affected workers in the hazard assessment and in the control or elimination of the hazards identified." | not fetched |

## Per hazard row

| Row | Alberta (Code Part, quoted numbers) | BC (Regulation Part, quoted numbers) |
|---|---|---|
| 1 Firearms | no Code provision found; federal Firearms Act applies; industry practice per CSATF #1/#2 | Actsafe bulletin MP-06-2024 "Firearms, Replicas, Blanks and Dummy Rounds"; Props Firearms Safety course. No WorkSafeBC numeric threshold. |
| 2 Pyro / explosives | Part 10 Fire and Explosion Hazards; Part 33 Explosives. Not fetched. | Part 21 Blasting Operations. No threshold fetched. |
| 3 Chemical | Part 4 Chemical Hazards; Part 29 WHMIS; Part 26 Ventilation. Not fetched. | Part 5 Chemical and Biological Substances. Reassessment trigger s.5.53(1) quoted above. |
| 4 Electrical | Part 17 Overhead Power Lines: requirements apply "within 7 metres of an overhead power line"; Schedule 4 voltage-distance table not fetched. Part 15 Control of Hazardous Energy. | Part 19 Electrical Safety. Not fetched. |
| 5 Pressure / pneumatic | Part 15; Part 25. Not fetched. | Part 12: compressed-air spray units "in excess of 70 kPa gauge (10 psig)" must meet specified conditions (s.12.139 area). |
| 6 Structural | Part 21 Rigging: inspection before use (s.294); load rating marked on sling (s.293); safety factors mandatory (s.292.1, values not fetched). Part 23 Scaffolds ss.323-353 not fetched. Part 30 Demolition. | Part 13 Scaffolds, Ladders, Temporary Work Platforms; Part 15 Rigging (definition confirmed). Numbers not fetched. |
| 7 Confined space | Part 5: oxygen "between 19.5% and 23.0% by volume" before entry; no entry above "20 percent of the lower explosive limit"; testing by a competent worker with calibrated instruments; entry permit (s.47); tending worker (s.56). | Part 9 Confined Spaces: written entry program, atmosphere classed low / moderate / high hazard. Numbers not fetched. |
| 8 Stunts (step ladder) | Part 2 assessment duty; Part 9 where height is involved. No stunt-specific Part. | Actsafe Motion Picture Bulletin #4 Stunts; Stunts Inspection Form; Stunt Safety Plan. |
| 9 Working at heights | Part 9: fall protection required at "3 metres or more"; arrest force limited to "6 kilonewtons", or "8 kilonewtons" with an E6 shock absorber; ladder cage from 2.4 m where ladder exceeds 6.1 m; anchor strength ss.152, 152.1 (kN not fetched); fall protection plan s.140. | Part 11 s.11.2(1)(a): "a fall protection system is used when work is being done at a place from which a fall of 3 m (10 ft) or more may occur." Anchors 22 kN (5,000 lbf) or 2x arrest force (WorkSafeBC hazard alert). Inspect before each shift and after any arrest; engineer recertifies after arrest. |
| 10 Power tools / machinery | Part 25 Tools, Equipment and Machinery; Part 22 Safeguards; Part 18 PPE. Not fetched. | Part 12 Tools, Machinery and Equipment (70 kPa line above). |
| 11 Motion | Part 19 Powered Mobile Equipment; Part 31 Diving. Not fetched. | Part 16 Mobile Equipment; Part 24 Diving. Not fetched. |
| 12 Environment | Part 6 s.106 "Wind and temperature limitations" for cranes exists; km/h value not fetched. Part 7 Emergency Preparedness. | Part 7 Thermal Environment: cold-stress provisions apply below core 36 °C or equivalent chill below -7 °C (Table 7-4), heated shelter required; heat by WBGT. Crane wind limits Part 14 not fetched. |

## Premises layer: fire, occupancy, electrical, pressure, permits

Enforced by different bodies than OHS, each with its own shutdown authority. The
jurisdiction pick includes the municipality because Vancouver's Charter lets it run its
own by-laws; Fire By-law 14419 carries 278 provisions unique to the city.

| Layer | Alberta | BC | Vancouver |
|---|---|---|---|
| Fire code | National Fire Code Alberta Edition 2023, in force May 1, 2024, under the Safety Codes Act; enforced by accredited municipal fire departments, Alberta Safety Codes Authority elsewhere | BC Fire Code 2024, in force March 8, 2024 | Fire By-law No. 14419; Vancouver Fire & Rescue, Fire Prevention office |
| Occupancy | National Building Code Alberta Edition 2023; occupant load posted permanently in a conspicuous location; temporary change of use rule not found | BC Building Code 2024 s.11.6 Temporary Buildings and Occupancies: temporary Group A Div 2 use in a Group F warehouse permitted with an occupant load plan "acceptable to the Fire Chief" | same, plus 14419 |
| Electrical | CSA C22.1-24 (26th ed.) adopted, effective April 1, 2025; permits via accredited municipality or agency | Technical Safety BC, Electrical Safety Regulation; Temporary Entertainment Installation Permit valid up to 14 days, renewable; "registered representative must request inspection whenever equipment is set up at any location" | Technical Safety BC |
| Pressure equipment | ABSA under the Safety Codes Act: pressure vessels, compressors, pressure piping. Air cannons and rams: scope not confirmed | Technical Safety BC Boiler & Pressure Vessel program; small air receivers may need label only. Air cannons and rams: scope not confirmed | Technical Safety BC |
| Film / pyro permit | Calgary: $5M liability with the City or CFD as additional insured; NRCan-certified technician with photo ID; Fire Safety Codes Officer present above 3-inch shells; site plan and fire safety plan; 7 to 10 days. Edmonton: NRCan-certified professionals only; Edmonton Fire Rescue; up to 10 working days | embedded in municipal fire permits | City Film & Special Events approves the effect, Fire Prevention issues a date-and-time-specific permit listing approved materials; high explosives copied to NRCan Explosives Regulatory Division; SFX coordinator may be asked for resume and references and the City may withhold; location manager arranges a site meeting |

Shutdown authority by layer: fire chief or safety codes officer (fire, occupancy);
electrical inspector or Technical Safety BC (electrical); ABSA or Technical Safety BC
(pressure); the city film office plus fire prevention (permits). Any one of them can
stop the scene independent of the OHS answer. Not found: Alberta fire-code text on
open flame indoors or fire watch; Alberta temporary change-of-use rule; Vancouver
By-law 14419 full text (fetch blocked).

## Welfare rows, headcount-driven

The call sheet's crew count and the distance to the nearest hospital are inputs. These
rows are quoted from the extracted Codes (`src/agent/query_code.py`).

| Row | Alberta | BC |
|---|---|---|
| First aid by headcount | Part 11 s.178: first aiders, supplies, kits, and room "in accordance with the applicable requirements of Schedule 2". Ratios are in Schedule 2, keyed by number of workers and travel time to a health-care facility. s.179 location; s.181 advanced first aider where required. | Part 3 s.3.16: at least what "Schedule 3-A" requires; s.3.17 written first aid procedures; s.3.18 communication between attendant and workers; s.3.19 records kept 3 years. |
| Drinking water | Part 24 s.355: "an adequate supply of drinking fluids … must include potable water." | Part 28 s.28.10: potable drinking water during the workday; Part 7 s.7.31 cool potable water close to the work area for heat-exposed workers; Part 4 s.4.87 non-potable sources must be signed. |
| Emergency response plan and contacts | Part 7 s.115: plan for emergencies requiring rescue or evacuation, workers involved; s.116 contents, including identification of emergencies, procedures, emergency equipment location; s.117 designated rescue and evacuation workers, trained; s.118 their equipment. | Part 5 s.5.101 written emergency response plan for hazardous substances; s.5.98 developed with workers; s.5.104 training and drills. General rescue/evacuation risk assessment in Part 4 s.4.13 (from earlier research; not yet quoted from extraction). |
| Food safety (catering, craft services) | Public Health Act Food Regulation AR 31/2006: food handling permit from the health authority; food handler certificate 5-year validity (AHS recognized courses). | Food Premises Regulation BC Reg 210/99 s.10: at least one FOODSAFE Level 1 (or equivalent) holder present during all preparation, storage, and service; FOODSAFE Level 1 expires 5 years from issue. |
| Rest turnaround (fatigue) | Employment Standards Code: 8 consecutive hours between shifts; work within a 12-hour window per day; 1 rest day per 6 worked. DGC Alberta 2026-28: 10-hour turnaround. IATSE 212 clause not retrieved. | Employment Standards Act s.36: 8 hours between shifts; 32 consecutive hours per week or 1.5x pay. BCCFU master agreement: 11-hour rest after turnaround encroached 2+ hours on 2 consecutive days (clause referenced, not quoted in full). |
| Rest turnaround, performers | ACTRA IPA 2025-27: 11 hours set-to-set; minors 12-15 yrs 12 hours set-to-set; under 12, 12 hours door-to-door; stunt coordinator 10 hours; breach paid at 200%. | same (national agreement) |
| Rest turnaround, US reference | SAG-AFTRA TV/Theatrical: 12 hours dismissal to next call; 10 hours on exterior location once per 4 consecutive days; forced-call penalty the lesser of daily rate or $900 (day performer). Not a Canadian rule; loaded only if jurisdiction is a US state. | |

Fatigue is on the timeline: Brent Hershman, 1997, Pleasantville, died driving home after
a 19-hour day following four 15-hour days. "Brent's Rule" proposed a 14-hour cap with
hotel accommodation past it; never adopted industry-wide. The escalation treats a call
sheet that breaches the loaded turnaround as AMBER for the department and RED for any
performer or driver on a Row 8 or Row 11 task that day.

## Certifications and retraining

Ticket validity differs by province, state, and issuing body. The agent takes the
shorter period when two apply. Blank = not sourced yet = treated as expired.

| Ticket / role | Alberta validity | BC validity | Source |
|---|---|---|---|
| Fall protection (worker) | 3 years by convention; no legislated refresher interval found (training-vendor source, not regulator) | 3 years, Actsafe course renewal | safetyevolution.com (vendor); actsafe.ca/courses-workshops/fall-protection/ |
| Confined space entry / tending | 3 years recertification (training-vendor convention aligned to Code Part 5) | not found in sources fetched | search-ohs-laws.alberta.ca Part 5 |
| First aid | 3 years, approved agency | 3 years, WorkSafeBC OFA; valid OFA certs accepted as equivalent from 2024-11-01 | worksafebc.com first-aid pages |
| Powered mobile equipment / forklift / AWP | 3 years by convention; employer certifies competence, no government licence | 3 years mandatory refresher, CSA B335-15 | safetyevolution.com (vendor) |
| Blaster (industrial) | Energy Safety Canada interprovincial permit; period not found | 5 years; 6 hours CPD annually | worksafebc.com/…/blasting |
| Crane operator | Alberta Apprenticeship trade certificate; validity not found | Provisional Level B 1 year, renewable once; full Level A validity not found | bccranesafety.ca |
| NCSO | 3-year cycle; annual maintenance: current first aid, WHMIS TTT, LSE proficiency renewal, one course per cycle, ACSA auditor status. Grandfathered rule not found in sources. | n/a | youracsa.ca/ncso-hsa/acsa-requirementsv2/ |
| PAL (federal) | 5 years; renewal notice 3 months before; 6-month grace after expiry | same, federal | rcmp.ca firearms licensing |
| Competent (Act definition) | OHS Act SA 2020 cO-2.2 s.1: "'competent' in relation to a person means adequately qualified, suitably trained and with sufficient experience to safely perform work without supervision or with only a minimal degree of supervision" (King's Printer, current as of June 11, 2025) | WorkSafeBC "qualified" definition, not yet pulled | kings-printer.alberta.ca |
| Professional engineer (certifies anchors, rigs, procedures) | APEGA licence, Code Part 3 s.14 | EGBC licence | Code s.14 (in `code.json`) |
| Crane / hoist operator | Code Part 6 (16 sections reference competence/certification); AB trade certification, period not pulled | Part 14; BC Crane Safety certification, period not pulled | |
| Blaster / pyrotechnician | Code Part 33 (7 sections); provincial blaster's permit, period not pulled | Part 21 blaster certificate, period not pulled; NRCan pyrotechnician card (federal) | |
| Confined space entrant / tester / tending worker | Code Part 5 (7 sections); training period not pulled | Part 9 training, period not pulled | |
| Powered mobile equipment operator | Code Part 19 (11 sections) | Part 16 | |
| Scaffold erector | Code Part 23 (11 sections) | Part 13 | |
| Firearms handler / armorer | federal PAL, or working under direct supervision of a PAL holder; no provincial film-armorer ticket found | same; Actsafe Props Firearms Safety course | actsafe.ca; bcfirearmsacademy.ca (vendor) |

## Gaps to close before the demo

- Alberta Part 6 s.106 crane wind limit and Part 9 anchor kN: pull from the Code PDF.
- Alberta Part 2 s.7 subsection numbering: confirm.
- BC Part 19 electrical, Part 16 mobile equipment, Part 14 crane wind: not fetched.
- Wind limits for condors, aerials, and exterior pyro: no public number in either
  jurisdiction's fetched text. These come from the NCSO's site practice and are
  labelled as such in the table the agent loads.

## Sources

- https://search-ohs-laws.alberta.ca/legislation/occupational-health-and-safety-code/part-2-hazard-assessment-elimination-and-control/
- https://search-ohs-laws.alberta.ca/legislation/occupational-health-and-safety-code/part-9-fall-protection/
- https://search-ohs-laws.alberta.ca/legislation/occupational-health-and-safety-code/part-5-confined-spaces/
- https://search-ohs-laws.alberta.ca/legislation/occupational-health-and-safety-code/part-6-cranes-hoists-and-lifting-devices/
- https://search-ohs-laws.alberta.ca/legislation/occupational-health-and-safety-code/part-17-overhead-power-lines/
- https://search-ohs-laws.alberta.ca/legislation/occupational-health-and-safety-code/part-21-rigging/
- https://www.bclaws.gov.bc.ca/civix/document/id/crbc/crbc/296_97_multi
- https://www.bclaws.gov.bc.ca/civix/document/id/loo61/loo61/296_97-05
- https://www.bclaws.gov.bc.ca/civix/document/id/loo61/loo61/296_97-07
- https://www.bclaws.gov.bc.ca/civix/document/id/loo62/loo62/296_97-09
- https://www.bclaws.gov.bc.ca/civix/document/id/loo61/loo61/296_97-11
- https://www.bclaws.gov.bc.ca/civix/document/id/loo60/loo60/296_97-12
- https://www.bclaws.gov.bc.ca/civix/document/id/loo61/loo61/296_97-15
- https://www.bclaws.gov.bc.ca/civix/document/id/loo69/loo69/23_296_97-21
- https://www.actsafe.ca/wp-content/uploads/2024/07/Firearms-Safety-Bulletin-1.pdf
- https://www.actsafe.ca/department/stunts/motion-picture-bulletin-stunts/
- https://actsafe.ca/safe-on-set/
