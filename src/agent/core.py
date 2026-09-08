import os
import asyncio
from pydantic import BaseModel
from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class StructuredResponse(BaseModel):
    message: str
    confidence: float

agent = Agent(
    name="test_agent",
    model=os.environ.get("GEMINI_MODEL", "gemini-3.7-flash"),
    instruction="Extract structured greeting from text.",
    output_schema=StructuredResponse,
    generate_content_config=types.GenerateContentConfig(temperature=0.0)
)

def main():
    runner = Runner(
        agent=agent,
        app_name="test_app",
        session_service=InMemorySessionService(),
        auto_create_session=True
    )
    
    events = runner.run(
        user_id="user1",
        session_id="session1",
        new_message=types.Content(role="user", parts=[types.Part.from_text(text="Say hello and give a confidence score.")])
    )
    
    for event in events:
        if getattr(event, "output", None):
            print("Output message:", getattr(event.output, "message", None))
            print("Output confidence:", getattr(event.output, "confidence", None))

if __name__ == "__main__":
    main()
