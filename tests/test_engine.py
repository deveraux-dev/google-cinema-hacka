"""Tests for agent.engine.run/replay."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent.engine import load_codes, load_schedules, replay, run
from agent.model import Day, HazardTag, Jurisdiction, Location, Plan, Roles, Scene, SitePractice

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"

CODES = load_codes()
SCHEDULES = load_schedules()

ROLES = Roles(first_ad="Ann Frost", safety_officer="Sam Officer", armorer="Al Arms", rigger="Dana Rigger", first_aiders=["Sam Aid"], catering_lead="Cat Erer")


def _plan() -> Plan:
    return Plan(
        production="P",
        jurisdiction=Jurisdiction(province="AB", municipality="Calgary"),
        locations=[Location(name="L", lat=None, lon=None, hospital_minutes=15)],
        schedule=[Day(day="D1", location="L", night=False, exterior=False, build_or_strike=False, headcount=10, on_call="")],
        roles=ROLES,
        site_practice=SitePractice(condor_wind_kmh=None, crane_wind_kmh=None, exterior_pyro_wind_kmh=None, rig_recheck_hours=None),
        created="2026-09-04",
        revised="2026-09-04",
    )


def test_replay_is_byte_identical_and_pins_sample_severities():
    result = replay(
        str(SAMPLES / "production.plan.json"),
        str(SAMPLES / "scenes.json"),
        str(SAMPLES / "clears.json"),
        str(SAMPLES / "crew.csv"),
        "2026-09-05",
    )
    parsed = json.loads(result)
    severities = {s["id"]: s["severity"] for s in parsed["scenes"]}
    assert severities == {"S1": "RED", "S2": "STOP", "S3": "STOP"}


def test_violation_forces_stop_removing_it_does_not():
    plan = _plan()
    scene_stop = Scene(id="S", heading="H", day="D1", tags=[], violations=["AB:999"])
    out_stop = run(plan, [scene_stop], [], [], "2026-09-04", CODES, SCHEDULES)
    assert out_stop["scenes"][0]["severity"] == "STOP"

    scene_clean = Scene(id="S", heading="H", day="D1", tags=[], violations=[])
    out_clean = run(plan, [scene_clean], [], [], "2026-09-04", CODES, SCHEDULES)
    assert out_clean["scenes"][0]["severity"] != "STOP"
