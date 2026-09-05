"""Tests for agent.locks hold/lock/verify/group and severity ladder."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent.locks import group_lock, open_hold, release, severity, verify
from agent.model import Requirement, Roles

ROLES = Roles(first_ad="Ann", safety_officer="Sam", armorer="Al", rigger="Rae", first_aiders=["Fi"], catering_lead="Cat")


def _req(row, section, kind):
    return Requirement(row=row, code=f"AB:{section}", part=9, section=section, heading="H", text="t", kind=kind)


def test_release_wrong_person_raises_and_owner_succeeds():
    state = {}
    reqs = [_req(9, "139", "must")]
    open_hold(state, "S1", reqs, ROLES)
    with pytest.raises(PermissionError):
        release(state, "S1", "first_ad", "Bob", "139", "2026-09-04")
    release(state, "S1", "first_ad", "Ann", "139", "2026-09-04")
    assert state["S1"]["locks"][0].released == "2026-09-04"


def test_verify_by_last_releaser_false_by_other_true():
    state = {}
    reqs = [_req(9, "139", "must")]
    open_hold(state, "S1", reqs, ROLES)
    release(state, "S1", "first_ad", "Ann", "139", "2026-09-04")
    assert verify(state, "S1", "Ann") is False
    assert verify(state, "S1", "Bob") is True


def test_group_lock_cannot_release_while_personal_lock_remains():
    state = {}
    reqs = [_req(9, "139", "must")]
    open_hold(state, "S1", reqs, ROLES)
    group_lock(state, "S1", "Dana")
    with pytest.raises(PermissionError):
        release(state, "S1", "on_call", "Dana", "GROUP", "2026-09-04")
    release(state, "S1", "first_ad", "Ann", "139", "2026-09-04")
    release(state, "S1", "on_call", "Dana", "GROUP", "2026-09-04")


def test_severity_ladder():
    state = {}
    reqs = [_req(9, "152", "engineer"), _req(9, "139", "must")]
    open_hold(state, "S1", reqs, ROLES)
    assert severity(state, "S1", reqs, {}) == "RED"
    release(state, "S1", "engineer", "Rae", "152", "2026-09-04")
    assert severity(state, "S1", reqs, {}) == "AMBER"
    release(state, "S1", "first_ad", "Ann", "139", "2026-09-04")
    assert severity(state, "S1", reqs, {}) == "GREEN"


def test_severity_stop_on_violation_or_register_missing():
    state = {}
    reqs = [_req(9, "139", "must")]
    open_hold(state, "S1", reqs, ROLES)
    assert severity(state, "S1", reqs, {}, violations=("AB:139",)) == "STOP"
    assert severity(state, "S1", reqs, {"first_aider": "missing"}) == "RED"
