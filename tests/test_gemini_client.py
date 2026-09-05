"""Tests for agent.gemini_client, mocked (no real key, no network)."""
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent import gemini_client

HAIKU = "Autumn wind through cranes / hazard rows count down to green / the wall goes quiet"


def test_missing_key_exits_2(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(SystemExit) as exc:
        gemini_client.call_gemini("hi")
    assert exc.value.code == 2


def test_call_gemini_returns_mocked_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

    class FakeModels:
        def generate_content(self, model, contents):
            return types.SimpleNamespace(text=HAIKU)

    class FakeClient:
        def __init__(self, api_key):
            self.models = FakeModels()

    fake_genai = types.ModuleType("google.genai")
    fake_genai.Client = FakeClient
    fake_google = types.ModuleType("google")
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)

    assert gemini_client.call_gemini("hi") == HAIKU
