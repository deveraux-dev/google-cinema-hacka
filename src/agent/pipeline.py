import os
import time
from google.adk import Agent
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv
from agent.models import DiffOutput, CascadeOutput, HazardTagOutput, Change, DepartmentDelta, HazardTag

load_dotenv()

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")
GENERATION_CONFIG = types.GenerateContentConfig(temperature=0.0)

# 1. Diff Agent
diff_instruction = """
Compare the original script text with the revised script text.
Identify all material changes (added, removed, or modified elements) such as heading, action, and dialogue.
Return a structured list of changes.
"""

diff_agent = Agent(
    name="diff_agent",
    model=MODEL_NAME,
    instruction=diff_instruction,
    output_schema=DiffOutput,
    generate_content_config=GENERATION_CONFIG
)

# 2. Cascade Agent
cascade_instruction = """
Review the script changes (Diff) provided.
Determine how these changes impact the workload or requirements of various production departments 
(e.g., Wardrobe, Set Dec, SPFX, Stunts, Grip, Lighting, Camera, Locations).
Return a structured list of department deltas.
"""

cascade_agent = Agent(
    name="cascade_agent",
    model=MODEL_NAME,
    instruction=cascade_instruction,
    output_schema=CascadeOutput,
    generate_content_config=GENERATION_CONFIG
)

# 3. Hazard Tag Agent
hazard_instruction = """
Review the script changes and departmental impacts.
Identify any hazards present in the scene and map them to the following Jurisdiction Hazard Rows (1-13):
1: Firearms
2: Pyro / explosives
3: Chemical
4: Electrical
5: Pressure / pneumatic
6: Structural / Scaffolds / Rigging
7: Confined space
8: Stunts
9: Working at heights (fall protection, >= 3 meters)
10: Power tools / machinery
11: Motion / Powered Mobile Equipment / Diving
12: Environment / Wind / Cold
13: Hazardous energy control (LOTO - servicing or resetting powered equipment)

Only apply a tag if the hazard is clearly introduced or present in the scene based on the text and deltas.
"""

hazard_agent = Agent(
    name="hazard_agent",
    model=MODEL_NAME,
    instruction=hazard_instruction,
    output_schema=HazardTagOutput,
    generate_content_config=GENERATION_CONFIG
)

class RevisionPipeline:
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.diff_runner = Runner(agent=diff_agent, app_name="ucs_pipeline", session_service=self.session_service, auto_create_session=True)
        self.cascade_runner = Runner(agent=cascade_agent, app_name="ucs_pipeline", session_service=self.session_service, auto_create_session=True)
        self.hazard_runner = Runner(agent=hazard_agent, app_name="ucs_pipeline", session_service=self.session_service, auto_create_session=True)

    def _run_agent(self, runner: Runner, prompt: str, session_id: str) -> any:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                events = runner.run(
                    user_id="system",
                    session_id=session_id,
                    new_message=types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
                )
                for event in events:
                    if getattr(event, "output", None):
                        return event.output
                    elif getattr(event, "content", None) and event.content.parts:
                        text = event.content.parts[0].text
                        if text:
                            return runner.agent.output_schema.model_validate_json(text)
                raise RuntimeError(f"Agent {runner.agent.name} failed to produce output.")
            except Exception as e:
                err_str = str(e)
                if ("503" in err_str or "429" in err_str or "RESOURCE_EXHAUSTED" in err_str) and attempt < max_retries - 1:
                    print(f"Temporary API limitation for {runner.agent.name}, retrying in 3s (attempt {attempt+1}/{max_retries})...")
                    time.sleep(3)
                else:
                    raise e

    def _offline_fallback(self, scene_id: str, original_text: str, revised_text: str):
        """
        Deterministic offline fallback extraction when remote Gemini API quota/network is unreachable.
        """
        print(f"[OFFLINE GOVERNANCE MODE] Evaluating scene {scene_id} via local deterministic rules...")
        changes = [
            Change(
                scene_id=scene_id,
                element="action",
                old_text=original_text.strip(),
                new_text=revised_text.strip()
            )
        ]
        
        deltas = []
        tags = []
        lower_rev = revised_text.lower()
        
        if "flash pot" in lower_rev or "explosion" in lower_rev or "pyro" in lower_rev:
            deltas.append(DepartmentDelta(department="SPFX", impact="Requires setup, perimeter clearance, and execution of practical pyrotechnics."))
            tags.append(HazardTag(row=2, label="pyro", detail="Practical pyrotechnic device / flash pot explosion introduced."))
            
        if "jump" in lower_rev or "stunt" in lower_rev or "fall" in lower_rev:
            deltas.append(DepartmentDelta(department="Stunts", impact="Stunt performer required for physical fall/jump action and deceleration mats."))
            tags.append(HazardTag(row=8, label="stunts", detail="Physical stunt action requiring coordinator walk-through."))
            
        if "20-foot" in lower_rev or "platform" in lower_rev or "scaffold" in lower_rev or "height" in lower_rev:
            deltas.append(DepartmentDelta(department="Grip / Rigging", impact="Fall protection and elevated platform rigging required."))
            tags.append(HazardTag(row=9, label="heights", detail="Elevated platform or fall hazard >= 3 metres requiring fall protection."))
            
        if "lift" in lower_rev or "hydraulic" in lower_rev or "crane" in lower_rev:
            deltas.append(DepartmentDelta(department="Grip", impact="Powered mobile equipment / hydraulic lift operation."))
            tags.append(HazardTag(row=11, label="motion_pme", detail="Powered mobile equipment / hydraulic lift."))
            tags.append(HazardTag(row=13, label="loto", detail="Hazardous energy isolation required before resetting equipment between takes."))

        if "gun" in lower_rev or "revolver" in lower_rev or "firearm" in lower_rev or "shot" in lower_rev or "blanks" in lower_rev:
            deltas.append(DepartmentDelta(department="Props / Armory", impact="Certified armorer required on set for blank-firing prop weapon."))
            tags.append(HazardTag(row=1, label="firearms", detail="Blank firearm discharge requiring direct armorer line-of-sight."))

        if "smoke" in lower_rev or "fog" in lower_rev or "watertight" in lower_rev or "compartment" in lower_rev:
            deltas.append(DepartmentDelta(department="SPFX / Safety", impact="Atmospheric fog in enclosed space requiring air quality monitoring."))
            tags.append(HazardTag(row=7, label="confined_space", detail="Enclosed compartment / restricted egress space."))

        if not deltas:
            deltas.append(DepartmentDelta(department="Production", impact="Dialogue / staging adjustment with standard set protocols."))

        return {
            "diff": DiffOutput(changes=changes),
            "cascade": CascadeOutput(scene_id=scene_id, deltas=deltas),
            "hazard_tags": HazardTagOutput(scene_id=scene_id, tags=tags)
        }

    def analyze_revision(self, scene_id: str, original_text: str, revised_text: str):
        print(f"Starting analysis for Scene {scene_id} with Gemini Model: {MODEL_NAME}...")
        
        try:
            # Step 1: DIFF
            diff_prompt = f"Original Script:\n{original_text}\n\nRevised Script:\n{revised_text}\n\nScene ID: {scene_id}"
            diff_output = self._run_agent(self.diff_runner, diff_prompt, f"diff_{scene_id}_{int(time.time())}")
            
            # Step 2: CASCADE
            cascade_prompt = f"Scene ID: {scene_id}\n\nScript Changes:\n{diff_output.model_dump_json(indent=2)}"
            cascade_output = self._run_agent(self.cascade_runner, cascade_prompt, f"cascade_{scene_id}_{int(time.time())}")
            
            # Step 3: HAZARD TAG
            hazard_prompt = f"Scene ID: {scene_id}\n\nScript Changes:\n{diff_output.model_dump_json(indent=2)}\n\nDepartment Impacts:\n{cascade_output.model_dump_json(indent=2)}"
            hazard_output = self._run_agent(self.hazard_runner, hazard_prompt, f"hazard_{scene_id}_{int(time.time())}")
            
            return {
                "diff": diff_output,
                "cascade": cascade_output,
                "hazard_tags": hazard_output
            }
        except Exception as e:
            print(f"Remote API warning ({e}). Engaging offline deterministic governance fallback...")
            return self._offline_fallback(scene_id, original_text, revised_text)
