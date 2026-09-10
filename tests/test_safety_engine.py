import pytest
from engine.safety import evaluate_safety

def test_safety_green_when_no_hazards():
    result = evaluate_safety([])
    assert result["severity"] == "GREEN"
    assert result["required_clears"] == []
    assert len(result["statutory_citations"]) >= 1
    assert result["statutory_citations"][0]["citation"] == "Alberta OHS Code Part 2, s.7(4)(c)"

def test_safety_red_for_pyro_and_heights():
    tags = [
        {"row": 2, "label": "pyro", "detail": "Explosion near dumpster"},
        {"row": 9, "label": "heights", "detail": "20ft jump from platform"}
    ]
    result = evaluate_safety(tags)
    assert result["severity"] == "RED"
    assert "SPFX Lead Clear" in result["required_clears"]
    assert "Key Rigger / Fall Protection Clear (Dana Rigger)" in result["required_clears"]
    assert "Safety Officer Clear (Sam Officer)" in result["required_clears"]
    assert any("Heights" in c.get("title", "") for c in result["statutory_citations"])

def test_safety_stop_on_firearms():
    tags = [
        {"row": 1, "label": "firearms", "detail": "Prop gun loaded with blanks"}
    ]
    result = evaluate_safety(tags)
    assert result["severity"] == "STOP"
    assert "Armorer Clear (Al Arms)" in result["required_clears"]

def test_safety_stop_on_explicit_violation():
    result = evaluate_safety([], explicit_violation=True)
    assert result["severity"] == "STOP"
    assert "Production Safety Manager Intervention" in result["required_clears"]
