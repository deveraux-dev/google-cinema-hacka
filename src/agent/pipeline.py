import os
from google.adk import Agent
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv
from agent.models import DiffOutput, CascadeOutput, HazardTagOutput

load_dotenv()

# Define the models model and configuration
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
        import time
        max_retries = 3
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
                            # Parse JSON into the Pydantic schema
                            return runner.agent.output_schema.model_validate_json(text)
                raise RuntimeError(f"Agent {runner.agent.name} failed to produce output.")
            except Exception as e:
                if "503 UNAVAILABLE" in str(e) and attempt < max_retries - 1:
                    print(f"503 UNAVAILABLE for {runner.agent.name}, retrying in 5 seconds (attempt {attempt+1}/{max_retries})...")
                    time.sleep(5)
                else:
                    raise e

    def analyze_revision(self, scene_id: str, original_text: str, revised_text: str):
        print(f"Starting analysis for Scene {scene_id}...")
        
        # Step 1: DIFF
        diff_prompt = f"Original Script:\n{original_text}\n\nRevised Script:\n{revised_text}\n\nScene ID: {scene_id}"
        diff_output = self._run_agent(self.diff_runner, diff_prompt, f"diff_{scene_id}")
        
        # Step 2: CASCADE
        cascade_prompt = f"Scene ID: {scene_id}\n\nScript Changes:\n{diff_output.model_dump_json(indent=2)}"
        cascade_output = self._run_agent(self.cascade_runner, cascade_prompt, f"cascade_{scene_id}")
        
        # Step 3: HAZARD TAG
        hazard_prompt = f"Scene ID: {scene_id}\n\nScript Changes:\n{diff_output.model_dump_json(indent=2)}\n\nDepartment Impacts:\n{cascade_output.model_dump_json(indent=2)}"
        hazard_output = self._run_agent(self.hazard_runner, hazard_prompt, f"hazard_{scene_id}")
        
        return {
            "diff": diff_output,
            "cascade": cascade_output,
            "hazard_tags": hazard_output
        }
