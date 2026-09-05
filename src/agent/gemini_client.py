"""Minimal Gemini call: google.genai.Client, GEMINI_API_KEY/GEMINI_MODEL from .env."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

DEFAULT_MODEL = "gemini-2.5-flash"


def call_gemini(prompt: str, model: str | None = None) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("GEMINI_API_KEY missing: online steps disabled", file=sys.stderr)
        sys.exit(2)
    import google.genai as genai

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model or os.environ.get("GEMINI_MODEL", DEFAULT_MODEL),
        contents=prompt,
    )
    return response.text


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "Say hello in one sentence."
    print(call_gemini(prompt))


if __name__ == "__main__":
    main()
