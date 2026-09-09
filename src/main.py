import os
import sys
import json
import asyncio
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Ensure we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.pipeline import MODEL_NAME, RevisionPipeline, has_gemini_credentials
from engine.safety import evaluate_safety
from engine.grafana_client import publish_to_grafana
from engine.db import log_run, get_latest_run

load_dotenv()

app = FastAPI(title="Universal CallSheet (UCS) - Production Safety Command Center")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(REPO_ROOT, "public")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
WRITE_STATIC_OUTPUT = os.environ.get("UCS_WRITE_STATIC_OUTPUT", "0") == "1"

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
    scenario_id: Optional[str] = Field(default="S1", max_length=80)
    scene_id: Optional[str] = Field(default="S1", max_length=80)
    scene_heading: Optional[str] = Field(default="EXT. LOADING DOCK - NIGHT", max_length=200)
    original_text: Optional[str] = Field(default=None, max_length=25_000)
    revised_text: Optional[str] = Field(default=None, max_length=25_000)
    trigger: str = Field(default="manual", max_length=40)


@app.get("/api/health")
async def get_health():
    grafana_remote = bool(os.environ.get("GRAFANA_MCP_URL"))
    grafana_local = bool(os.environ.get("GRAFANA_URL"))
    return {
        "status": "ok",
        "analysis": {
            "provider": "google_adk_gemini",
            "configured": has_gemini_credentials(),
            "model": MODEL_NAME,
            "fallback_available": True,
        },
        "safety": {"engine": "deterministic_python", "configured": True},
        "grafana": {
            "configured": grafana_remote or grafana_local,
            "transport": "streamable_http" if grafana_remote else "stdio" if grafana_local else "disabled",
        },
        "frontend": {"json_contract": "v1", "same_origin_api": True},
    }

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
    adk_result = await run_in_threadpool(
        pipeline.analyze_revision, scene_id, original_text, revised_text
    )
    
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
        "tagline": "Structured script revision analysis and deterministic safety governance for film production.",
        "production_context": PRODUCTION_CONTEXT,
        "jurisdiction": "Alberta OHS Code (AR 191/2021) / Section 7(4)(c)",
        "model_primary": MODEL_NAME,
        "analysis": {
            "mode": analysis_mode,
            "note": analysis_note,
            "fallback_reason": adk_result.get("fallback_reason"),
            "provider_attempted": adk_result.get("provider_attempted", False),
            "structured_output_order": ["DiffOutput", "CascadeOutput", "HazardTagOutput"],
            "deterministic_decision_owner": "engine.safety.evaluate_safety"
        },
        "runtime": {
            "delivery": "live_request",
            "api": "fastapi",
            "json_contract": "v1",
            "trigger": req.trigger if req.trigger in {"manual", "auto_review"} else "manual",
            "automation": "auto_review" if req.trigger == "auto_review" else "user_requested",
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
    
    # Persistence is best effort. Vercel's deployed bundle is read-only and its /tmp
    # filesystem is ephemeral, so the live response must never depend on either write.
    try:
        log_run(final_output)
    except (OSError, sqlite3.Error) as exc:
        print(f"Run history unavailable: {exc.__class__.__name__}")

    if WRITE_STATIC_OUTPUT:
        try:
            os.makedirs(PUBLIC_DIR, exist_ok=True)
            with open(os.path.join(PUBLIC_DIR, "output.json"), "w", encoding="utf-8") as output_file:
                json.dump(final_output, output_file, indent=2)
        except OSError as exc:
            print(f"Static output cache unavailable: {exc.__class__.__name__}")
        
    return final_output

@app.get("/api/latest")
async def get_latest():
    try:
        latest = get_latest_run()
    except (OSError, sqlite3.Error):
        latest = None
    if latest:
        latest["runtime"] = {
            "delivery": "history_snapshot",
            "api": "fastapi",
            "json_contract": "v1",
        }
        return latest
    if not latest:
        # Fallback to output.json
        try:
            with open(os.path.join(PUBLIC_DIR, "output.json"), "r", encoding="utf-8") as f:
                snapshot = json.load(f)
                snapshot["runtime"] = {
                    "delivery": "static_snapshot",
                    "api": "fastapi",
                    "json_contract": "v1",
                }
                return snapshot
        except Exception:
            raise HTTPException(status_code=404, detail="No historical runs found.")

# Mount assets before the catch-all public route so the branded UI works on the
# same origin in local FastAPI and Vercel deployments.
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
if os.path.exists(PUBLIC_DIR):
    app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
