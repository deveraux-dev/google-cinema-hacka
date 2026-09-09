import os
import sys
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.pipeline import RevisionPipeline
from engine.safety import evaluate_safety
from engine.grafana_client import publish_to_grafana
from engine.db import log_run, get_latest_run

load_dotenv()

app = FastAPI(title="Universal CallSheet (UCS) - Production Safety Command Center")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(REPO_ROOT, "public")

# Production Metadata from samples/production.plan.json
PRODUCTION_CONTEXT = {
    "production_name": "Backlot Test: Sovereign Stage 4",
    "call_sheet_day": "Day 2 of 42 (Night Exterior)",
    "location": {
        "name": "Warehouse 9 / Backlot Stage",
        "hospital_minutes": 15,
        "nearest_hospital": "Foothills Medical Centre (Level 1 Trauma)"
    },
    "crew_on_duty": {
        "first_ad": "Ann Frost",
        "safety_officer": "Sam Officer",
        "armorer": "Al Arms",
        "rigger": "Dana Rigger",
        "first_aider": "Sam Aid",
        "headcount": 42
    },
    "jurisdiction": {
        "code": "AB",
        "name": "Alberta OHS Code (AR 191/2021 current to 2025-03-31)",
        "secondary": "WorkSafeBC (BC Reg 296/97)"
    },
    "site_conditions": {
        "temperature": "12°C",
        "wind_speed_kmh": 22,
        "wind_threshold_kmh": 40,
        "status": "GREEN / WITHIN SAFE LIMITS"
    }
}

PRELOADED_SCENARIOS = {
    "S1": {
        "id": "S1",
        "title": "Night Stunt Jump & Flash Pot Explosion",
        "heading": "EXT. LOADING DOCK - NIGHT",
        "description": "High-risk action rewrite adding practical pyrotechnics, a 20-foot performer fall, and powered hydraulic lift resets.",
        "expected_severity": "RED",
        "original_text": """[Scene 1] EXT. LOADING DOCK - NIGHT
The loading dock is quiet. A security guard walks past holding a flashlight.""",
        "revised_text": """[Scene 1] EXT. LOADING DOCK - NIGHT
The loading dock is quiet. A security guard walks past holding a flashlight.
Suddenly, a pyrotechnic flash pot explodes near the dumpster.
A masked performer jumps from a 20-foot elevated platform down to the concrete, rolling to safety.
The crew resets the powered hydraulic lift between takes."""
    },
    "S2": {
        "id": "S2",
        "title": "Confined Space Prop Firearm Shootout",
        "heading": "INT. CARGO HOLD - NIGHT",
        "description": "Interior hull revision introducing blank firearm discharge and restricted egress atmospheric fog.",
        "expected_severity": "STOP",
        "original_text": """[Scene 2] INT. CARGO HOLD - NIGHT
John and Sarah search through the storage crates under low emergency lighting.""",
        "revised_text": """[Scene 2] INT. CARGO HOLD - NIGHT
John and Sarah search through the storage crates under low emergency lighting.
Heavy atmospheric smoke fills the sealed watertight compartment.
John draws a prop revolver loaded with quarter-load blanks and fires two shots toward the hatch."""
    },
    "S3": {
        "id": "S3",
        "title": "Aerial High-Wind Crane Rigging",
        "heading": "EXT. ROOFTOP - NIGHT",
        "description": "Exterior rooftop stunt featuring a 60-foot condor crane flying rig in gusty night weather.",
        "expected_severity": "RED",
        "original_text": """[Scene 3] EXT. ROOFTOP - NIGHT
Elena looks out over the city skyline from behind the perimeter railing.""",
        "revised_text": """[Scene 3] EXT. ROOFTOP - NIGHT
Elena steps past the perimeter railing onto an exterior scaffold.
A 60-foot telescopic condor crane hoists a stunt performer into high-altitude wind gusts over the edge."""
    },
    "S4": {
        "id": "S4",
        "title": "Routine Office Dialogue Revision",
        "heading": "INT. PRODUCTION OFFICE - DAY",
        "description": "Standard character and dialogue adjustments with zero physical risk or hazardous machinery.",
        "expected_severity": "GREEN",
        "original_text": """[Scene 4] INT. PRODUCTION OFFICE - DAY
David reviews the schedule on his laptop while drinking coffee.""",
        "revised_text": """[Scene 4] INT. PRODUCTION OFFICE - DAY
David reviews the revised call sheet on his tablet.
SARAH walks in holding two coffees, setting one on the desk with a smile."""
    }
}

class AnalyzeRequest(BaseModel):
    scenario_id: Optional[str] = "S1"
    scene_id: Optional[str] = "S1"
    scene_heading: Optional[str] = "EXT. LOADING DOCK - NIGHT"
    original_text: Optional[str] = None
    revised_text: Optional[str] = None

@app.get("/api/context")
async def get_production_context():
    return PRODUCTION_CONTEXT

@app.get("/api/scenarios")
async def get_scenarios():
    return list(PRELOADED_SCENARIOS.values())

@app.post("/api/analyze")
async def analyze_scene(req: AnalyzeRequest):
    print(f"Executing Universal CallSheet analysis for Scenario/Scene {req.scenario_id or req.scene_id}...")
    
    # Resolve script texts
    if req.scenario_id and req.scenario_id in PRELOADED_SCENARIOS:
        scenario = PRELOADED_SCENARIOS[req.scenario_id]
        scene_id = scenario["id"]
        scene_heading = scenario["heading"]
        original_text = req.original_text or scenario["original_text"]
        revised_text = req.revised_text or scenario["revised_text"]
    else:
        scene_id = req.scene_id or "CUSTOM"
        scene_heading = req.scene_heading or "SCENE REVISION"
        original_text = req.original_text or PRELOADED_SCENARIOS["S1"]["original_text"]
        revised_text = req.revised_text or PRELOADED_SCENARIOS["S1"]["revised_text"]

    # Step 1: Gemini / Google ADK Extraction
    pipeline = RevisionPipeline()
    adk_result = pipeline.analyze_revision(scene_id, original_text, revised_text)
    
    diff_output = adk_result["diff"].model_dump()
    cascade_output = adk_result["cascade"].model_dump()
    hazard_output = adk_result["hazard_tags"].model_dump()
    analysis_mode = adk_result.get("analysis_mode", "google_adk_gemini")
    analysis_note = adk_result.get("analysis_note", "Structured analysis completed.")
    
    hazard_tags = hazard_output.get("tags", [])
    
    # Step 2: Deterministic Safety Engine (Alberta OHS Code)
    safety_result = evaluate_safety(hazard_tags=hazard_tags)
    
    # Step 3: Grafana MCP Notification
    labels = [tag.get("label", "") for tag in hazard_tags]
    grafana_result = await publish_to_grafana(
        scene_id=scene_id,
        severity=safety_result["severity"],
        hazard_labels=labels,
        required_clears=safety_result["required_clears"]
    )
    
    # Step 4: Compile Final Production Record
    final_output = {
        "project": "Universal CallSheet",
        "tagline": "Deterministic script revision cascades and offline safety governance for film production.",
        "production_context": PRODUCTION_CONTEXT,
        "jurisdiction": "Alberta OHS Code (AR 191/2021) / Section 7(4)(c)",
        "model_primary": os.environ.get("GEMINI_MODEL", "gemini-3.7-flash"),
        "model_reviewer": "gemini-3.1-flash", 
        "analysis": {
            "mode": analysis_mode,
            "note": analysis_note,
            "structured_output_order": ["DiffOutput", "CascadeOutput", "HazardTagOutput"],
            "deterministic_decision_owner": "engine.safety.evaluate_safety"
        },
        "scene": {
            "id": scene_id,
            "heading": scene_heading,
            "original_script": original_text,
            "revised_script": revised_text
        },
        "diff": diff_output.get("changes", []),
        "department_deltas": cascade_output.get("deltas", []),
        "hazard_tags": hazard_tags,
        "safety": safety_result,
        "grafana": grafana_result
    }
    
    # Log to SQLite
    log_run(final_output)
    
    # Write to output.json for static caching
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    with open(os.path.join(PUBLIC_DIR, "output.json"), "w") as f:
        json.dump(final_output, f, indent=2)
        
    return final_output

@app.get("/api/latest")
async def get_latest():
    latest = get_latest_run()
    if not latest:
        # Fallback to output.json
        try:
            with open(os.path.join(PUBLIC_DIR, "output.json"), "r") as f:
                return json.load(f)
        except Exception:
            raise HTTPException(status_code=404, detail="No historical runs found.")
    return latest

# Mount static files (this serves public/index.html on /)
app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
