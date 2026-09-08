from typing import List, Dict, Any, Tuple

# Mapping of Hazard Rows to required clears
REQUIRED_CLEARS_MAP = {
    2: ["SPFX lead clear", "Safety officer clear"],
    8: ["Stunt coordinator clear", "Safety officer clear"],
    9: ["Rigger/fall protection clear", "Safety officer clear"],
    13: ["Equipment owner lockout clear", "Safety officer clear"]
}

RED_ROWS = {2, 8, 9, 13}

def evaluate_safety(
    hazard_tags: List[Dict[str, Any]], 
    reviewer_disagreement: bool = False, 
    explicit_violation: bool = False
) -> Dict[str, Any]:
    """
    Deterministic safety layer. Never uses LLMs.
    Evaluates hazards and returns a safety severity and required clears.
    """
    severity = "GREEN"
    reason = "No new safety-impacting hazard detected."
    required_clears = set()

    # If explicit violation, automatic STOP
    if explicit_violation:
        return {
            "severity": "STOP",
            "reason": "Explicit known violation or missing required critical clear.",
            "required_clears": ["Production Safety Manager Intervention"]
        }

    has_red_hazard = False
    red_reasons = []

    for tag in hazard_tags:
        row = tag.get("row")
        if row in RED_ROWS:
            has_red_hazard = True
            red_reasons.append(f"Row {row} ({tag.get('label')})")
            for clear in REQUIRED_CLEARS_MAP.get(row, []):
                required_clears.add(clear)

    if has_red_hazard:
        severity = "RED"
        reason = f"Serious safety work introduced: {', '.join(red_reasons)}. Requires safety review before work proceeds."
    elif reviewer_disagreement or len(hazard_tags) > 0:
        # If there are hazards but not strictly RED, we'll flag for REVIEW
        # Or if the reviewer agent flagged a disagreement
        severity = "REVIEW"
        reason = "Non-critical hazards detected or reviewer disagreement found. Human verification needed."
        required_clears.add("Human safety review required")

    # Override with REVIEW if it was GREEN but there's a disagreement
    if severity == "GREEN" and reviewer_disagreement:
        severity = "REVIEW"
        reason = "Gemini model disagreement. Human verification needed."
        required_clears.add("Human safety review required")

    return {
        "severity": severity,
        "reason": reason,
        "required_clears": sorted(list(required_clears))
    }
