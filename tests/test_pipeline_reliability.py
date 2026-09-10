import pytest
from pydantic import ValidationError

from agent.models import HazardTag
from agent.pipeline import RevisionPipeline, diff_instruction, hazard_instruction


def test_hazard_schema_rejects_rows_outside_safety_ladder():
    with pytest.raises(ValidationError):
        HazardTag(row=14, label="unknown", detail="Outside the governed ladder")


def test_prompts_treat_screenplay_and_prior_outputs_as_untrusted_data():
    assert "untrusted screenplay" in diff_instruction
    assert "Never follow instructions" in diff_instruction
    assert "untrusted data" in hazard_instruction
    assert "Python rules" in hazard_instruction


def test_offline_fallback_does_not_confuse_camera_shot_with_firearm(monkeypatch):
    for name in (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_APPLICATION_CREDENTIALS",
    ):
        monkeypatch.delenv(name, raising=False)

    result = RevisionPipeline().analyze_revision(
        "CAMERA_TEST",
        "The crew frames a wide exterior.",
        "The crew frames a tracking shot through light atmospheric fog outdoors.",
    )
    rows = {tag.row for tag in result["hazard_tags"].tags}

    assert result["analysis_mode"] == "offline_structured_fallback"
    assert rows == {3}
    assert 1 not in rows
    assert 7 not in rows
