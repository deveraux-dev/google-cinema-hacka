import os
import sys
import json
import asyncio
from dotenv import load_dotenv

# Ensure we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.pipeline import RevisionPipeline
from engine.safety import evaluate_safety
from engine.grafana_client import publish_to_grafana

load_dotenv()

async def main():
    print("Starting Universal CallSheet (UCS) Hackathon Proof Path...")
    
    # 1. Define Demo Scenario
    scene_id = "S1"
    scene_heading = "EXT. LOADING DOCK - NIGHT"
    
    original_text = """
[Scene 1] EXT. LOADING DOCK - NIGHT
The loading dock is quiet. A security guard walks past.
    """
    
    revised_text = """
[Scene 1] EXT. LOADING DOCK - NIGHT
The loading dock is quiet. A security guard walks past. 
Suddenly, a flash pot explodes near the dumpster. 
A masked performer jumps from a 20-foot elevated platform down to the concrete, rolling to safety.
The crew resets the powered hydraulic lift between takes.
    """
    
    print("\n--- 1. Gemini/ADK Extraction ---")
    pipeline = RevisionPipeline()
    adk_result = pipeline.analyze_revision(scene_id, original_text, revised_text)
    
    diff_output = adk_result["diff"].model_dump()
    cascade_output = adk_result["cascade"].model_dump()
    hazard_output = adk_result["hazard_tags"].model_dump()
    
    # 2. Deterministic Safety Status
    print("\n--- 2. Deterministic Safety Layer ---")
    hazard_tags = hazard_output.get("tags", [])
    
    # Check if there was any model disagreement flagged (we'll assume False for this pure vertical slice unless tags are empty)
    safety_result = evaluate_safety(hazard_tags=hazard_tags)
    
    print(f"Severity: {safety_result['severity']}")
    print(f"Reason: {safety_result['reason']}")
    print(f"Required Clears: {safety_result['required_clears']}")
    
    # 3. Grafana MCP Update
    print("\n--- 3. Grafana MCP Publish ---")
    labels = [tag.get("label", "") for tag in hazard_tags]
    grafana_result = await publish_to_grafana(
        scene_id=scene_id,
        severity=safety_result["severity"],
        hazard_labels=labels,
        required_clears=safety_result["required_clears"]
    )
    
    print(f"Grafana Publish Status: {grafana_result['published']}")
    if grafana_result['error']:
        print(f"Grafana Note/Error: {grafana_result['error']}")
    
    # 4. Compile Final JSON
    final_output = {
        "project": "Universal CallSheet",
        "tagline": "Deterministic script revision cascades and offline safety governance for film production.",
        "jurisdiction": "AB",
        "model_primary": os.environ.get("GEMINI_MODEL", "gemini-3.7-flash"),
        "model_reviewer": "gemini-3.1-flash", # Placeholder for the 80/20 slice
        "scene": {
            "id": scene_id,
            "heading": scene_heading
        },
        "diff": diff_output.get("changes", []),
        "department_deltas": cascade_output.get("deltas", []),
        "hazard_tags": hazard_tags,
        "safety": safety_result,
        "grafana": grafana_result
    }
    
    # Ensure public directory exists
    os.makedirs("public", exist_ok=True)
    
    output_path = os.path.join("public", "output.json")
    with open(output_path, "w") as f:
        json.dump(final_output, f, indent=2)
        
    print(f"\n--- 4. Success! Wrote static output to {output_path} ---")

if __name__ == "__main__":
    asyncio.run(main())
