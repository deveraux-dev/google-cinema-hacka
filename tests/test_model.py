"""Tests for agent.model.load_plan."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent.model import load_plan

TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "production.template.json"


def test_load_plan_missing_jurisdiction_raises(tmp_path):
    with pytest.raises(ValueError, match="jurisdiction required"):
        load_plan(str(TEMPLATE))


def test_load_plan_with_province_ab_loads(tmp_path):
    raw = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    raw["jurisdiction"]["province"] = "AB"
    out = tmp_path / "plan.json"
    out.write_text(json.dumps(raw), encoding="utf-8")
    plan = load_plan(str(out))
    assert plan.jurisdiction.province == "AB"


def test_load_plan_unknown_province_raises(tmp_path):
    raw = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    raw["jurisdiction"]["province"] = "ON"
    out = tmp_path / "plan.json"
    out.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown province"):
        load_plan(str(out))
