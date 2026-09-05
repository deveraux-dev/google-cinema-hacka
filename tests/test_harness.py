"""Tests for agent.harness._run against the sample fixtures."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent.harness import DEFAULT_SAMPLES, _run


def test_run_matches_engine_cli_shape():
    out = _run(DEFAULT_SAMPLES, "2026-09-05")
    assert out["production"] == "Backlot Test"
    assert {s["id"] for s in out["scenes"]} == {"S1", "S2", "S3"}


def test_missing_sample_file_raises():
    bad = dict(DEFAULT_SAMPLES)
    bad["plan"] = Path("does-not-exist.json")
    try:
        _run(bad, "2026-09-05")
        raised = False
    except FileNotFoundError:
        raised = True
    assert raised
