"""Tests for agent.first_aid Schedule 2 lookup."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent.first_aid import first_aid_requirement
from agent.model import Day

SCHEDULES = json.loads((Path(__file__).resolve().parents[1] / "data" / "alberta-ohs" / "schedules.json").read_text(encoding="utf-8"))


def _day(headcount: int, build_or_strike: bool = False) -> Day:
    return Day(day="D1", location="L", night=False, exterior=False, build_or_strike=build_or_strike, headcount=headcount, on_call="")


def test_shoot_day_close_medium_table6():
    out = first_aid_requirement(_day(30), [], 15, SCHEDULES)
    assert out["table"] == 6
    assert out["class"] == "medium"
    assert out["band"] == "close"
    assert out["requirement"] == (
        "1 Basic First Aider | | 1 Intermediate First Aider | | CSA Standard Z1220-17 Type 2 Basic Medium First Aid Kit"
    )


def test_build_or_strike_uses_table7():
    out = first_aid_requirement(_day(30, build_or_strike=True), [], 15, SCHEDULES)
    assert out["table"] == 7
    assert out["class"] == "high"


def test_isolated_hospital_changes_cell_text():
    close = first_aid_requirement(_day(30), [], 15, SCHEDULES)
    isolated = first_aid_requirement(_day(30), [], 45, SCHEDULES)
    assert isolated["band"] == "isolated"
    assert isolated["requirement"] != close["requirement"]


def test_bc_returns_unresolved_stub():
    out = first_aid_requirement(_day(30), [], 15, None)
    assert out == {"table": "3-A", "requirement": "Schedule 3-A not yet extracted", "unresolved": True}


def test_table1_low_hazard_has_no_film_category():
    table1 = next(t for t in SCHEDULES if t["schedule"] == 2 and t["table"] == 1)
    assert not any("film" in cell.lower() for row in table1["rows"] for cell in row)
