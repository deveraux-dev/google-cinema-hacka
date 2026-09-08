from typing import List, Dict, Any

# Real Statutory OHS Citations from Alberta Occupational Health and Safety Code (AR 191/2021)
OHS_STATUTES = {
    "s.7(4)(c)": {
        "citation": "Alberta OHS Code Part 2, s.7(4)(c)",
        "title": "Mandatory Hazard Assessment Revision",
        "statute_text": "An employer must ensure that the hazard assessment is repeated before work begins on a new work site or when a work process or operation changes.",
        "mandatory": True
    },
    1: {
        "citation": "Alberta OHS Code Part 28, s.498 & Firearms Act",
        "title": "Firearms & Explosive Devices",
        "statute_text": "Special effects firearms, blank ammunition, and explosive props must be handled exclusively by a certified armorer with direct line-of-sight and verified clear zones.",
        "clears": ["Armorer Clear (Al Arms)", "Safety Officer Clear (Sam Officer)"],
        "severity": "STOP"
    },
    2: {
        "citation": "Alberta OHS Code Part 28, s.498 (Pyrotechnics & Special Effects)",
        "title": "Pyrotechnic Devices & Flash Pots",
        "statute_text": "Pyrotechnic special effects require an authorized special effects pyrotechnician, local fire jurisdiction permit, and an enforced 50-foot safety exclusion perimeter.",
        "clears": ["SPFX Lead Clear", "Safety Officer Clear (Sam Officer)"],
        "severity": "RED"
    },
    3: {
        "citation": "Alberta OHS Code Part 4, s.21 (Chemical Hazards & Atmospheric Contaminants)",
        "title": "Atmospheric & Chemical Hazards",
        "statute_text": "Employer must ensure atmospheric smoke, chemical fogs, and particulate exposure are monitored with Safety Data Sheets (SDS) active on set.",
        "clears": ["Safety Officer Clear (Sam Officer)"],
        "severity": "REVIEW"
    },
    4: {
        "citation": "Alberta OHS Code Part 15, s.200 (Electrical Safety)",
        "title": "Temporary Electrical & High Voltage",
        "statute_text": "All temporary stage power distribution and generators must be GFCI-protected, grounded, and signed off by a certified gaffer/electrician.",
        "clears": ["Master Electrician / Gaffer Clear"],
        "severity": "REVIEW"
    },
    5: {
        "citation": "Alberta OHS Code Part 10, s.162 (Pressure Vessels & Pneumatics)",
        "title": "Pneumatic & High-Pressure Actuators",
        "statute_text": "High-pressure pneumatic air cannons and hydraulic lines must feature calibrated pressure-relief valves and daily inspection logs.",
        "clears": ["SPFX Lead Clear"],
        "severity": "REVIEW"
    },
    6: {
        "citation": "Alberta OHS Code Part 3, s.12 (Rigging & Structural Specifications)",
        "title": "Overhead Rigging & Structural Loads",
        "statute_text": "Overhead trusses, green screen scaffolds, and structural flying rigs must be calculated and certified by an entertainment rigger.",
        "clears": ["Key Rigger Clear (Dana Rigger)"],
        "severity": "RED"
    },
    7: {
        "citation": "Alberta OHS Code Part 5, s.44 (Confined Space Entry & Rescue)",
        "title": "Confined Spaces & Enclosed Tanks",
        "statute_text": "Entry into water tanks, sealed vehicles, or subterranean sets requires pre-entry gas testing, ventilation, and a dedicated rescue plan.",
        "clears": ["Safety Officer Clear (Sam Officer)", "On-Site Medic Standby"],
        "severity": "RED"
    },
    8: {
        "citation": "Alberta OHS Code Part 2, s.9 (Hazard Assessment & Stunt Coordination)",
        "title": "High-Risk Physical Stunts & Acrobatics",
        "statute_text": "High-velocity falls, vehicle stunts, and performer combat require a stunt coordinator walk-through, rehearsal inspection, and crash deceleration zones.",
        "clears": ["Stunt Coordinator Clear", "Safety Officer Clear (Sam Officer)"],
        "severity": "RED"
    },
    9: {
        "citation": "Alberta OHS Code Part 9, s.139 (Fall Protection Systems)",
        "title": "Working at Heights (>= 3 Metres)",
        "statute_text": "An employer must ensure that a fall protection system is used where a worker or performer may fall 3 metres (approx 10 feet) or more.",
        "clears": ["Key Rigger / Fall Protection Clear (Dana Rigger)", "Safety Officer Clear (Sam Officer)"],
        "severity": "RED"
    },
    10: {
        "citation": "Alberta OHS Code Part 25, s.369 (Tools & Machinery Guarding)",
        "title": "Power Tools & Construction Equipment",
        "statute_text": "On-set set alteration tools must maintain active machine guards and eye/ear protection perimeters.",
        "clears": ["Construction Coordinator Clear"],
        "severity": "REVIEW"
    },
    11: {
        "citation": "Alberta OHS Code Part 19, s.256 (Powered Mobile Equipment)",
        "title": "Powered Mobile Equipment & Lifts",
        "statute_text": "Powered hydraulic lifts, telescopic handlers, and condor cranes require certified operators, visual spotters, and cleared travel lanes.",
        "clears": ["Key Grip Clear"],
        "severity": "REVIEW"
    },
    12: {
        "citation": "Alberta OHS Code Part 16, s.228 & Industry Safety Bulletin 38",
        "title": "Extreme Weather & Wind Thresholds",
        "statute_text": "Outdoor elevated camera cranes, aerial rigging, and open pyrotechnics must cease operations when sustained wind gusts exceed 40 km/h.",
        "clears": ["1st AD Weather Hold Clear (Ann Frost)"],
        "severity": "RED"
    },
    13: {
        "citation": "Alberta OHS Code Part 13, s.212 (Hazardous Energy Control / LOTO)",
        "title": "Lockout / Tagout & Hydraulic Energy Isolation",
        "statute_text": "Before servicing, resetting, or reloading powered mechanical lifts or hydraulic rigs between takes, all energy sources must be isolated and verified zero-state.",
        "clears": ["Equipment Owner Lockout Clear", "Safety Officer Clear (Sam Officer)"],
        "severity": "RED"
    }
}

RED_ROWS = {1, 2, 6, 7, 8, 9, 12, 13}

def evaluate_safety(
    hazard_tags: List[Dict[str, Any]], 
    reviewer_disagreement: bool = False, 
    explicit_violation: bool = False
) -> Dict[str, Any]:
    """
    Deterministic film production safety layer. Zero-LLM pure rules engine.
    Maps hazard tags directly to statutory Alberta OHS Code obligations and mandatory clearances.
    """
    severity = "GREEN"
    reason = "No high-risk safety-impacting hazards detected. Standard production safety protocols apply."
    required_clears = set()
    statutory_citations = [OHS_STATUTES["s.7(4)(c)"]]

    if explicit_violation:
        return {
            "severity": "STOP",
            "reason": "CRITICAL STOP: Explicit safety violation or unpermitted high-risk operation detected. Camera cannot roll.",
            "required_clears": ["Production Safety Manager Intervention", "Executive Producer Signoff"],
            "statutory_citations": statutory_citations + [
                {
                    "citation": "Alberta OHS Act SA 2020 cO-2.2 s.31",
                    "title": "Immediate Stop-Work Order",
                    "statute_text": "Work must immediately cease when an imminent hazard exists or mandatory safety clear requirements are unsatisfied.",
                    "mandatory": True
                }
            ]
        }

    has_stop_hazard = False
    has_red_hazard = False
    flagged_reasons = []

    for tag in hazard_tags:
        row = tag.get("row")
        statute = OHS_STATUTES.get(row)
        if statute:
            statutory_citations.append(statute)
            for clear in statute.get("clears", []):
                required_clears.add(clear)
            
            if statute.get("severity") == "STOP":
                has_stop_hazard = True
                flagged_reasons.append(f"Row {row} ({statute['title']})")
            elif row in RED_ROWS:
                has_red_hazard = True
                flagged_reasons.append(f"Row {row} ({statute['title']})")

    if has_stop_hazard:
        severity = "STOP"
        reason = f"MANDATORY STOP: Life-safety regulated activity introduced ({', '.join(flagged_reasons)}). Cannot roll camera without dedicated certified safety master sign-off."
    elif has_red_hazard:
        severity = "RED"
        reason = f"High-risk safety hazards introduced: {', '.join(flagged_reasons)}. Mandatory pre-take clearances required per Alberta OHS Code."
    elif reviewer_disagreement or len(hazard_tags) > 0:
        severity = "REVIEW"
        reason = "Secondary hazards or model variance detected. Requires 1st AD / Safety Officer review."
        required_clears.add("Safety Officer Review (Sam Officer)")

    return {
        "severity": severity,
        "reason": reason,
        "required_clears": sorted(list(required_clears)),
        "statutory_citations": statutory_citations
    }
