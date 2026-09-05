"""Tests for agent.routing.route and classify."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent.model import HazardTag, Scene
from agent.routing import ROUTES, route

ROOT = Path(__file__).resolve().parents[1]
CODES = {
    "AB": json.loads((ROOT / "data" / "alberta-ohs" / "code.json").read_text(encoding="utf-8")),
    "BC": json.loads((ROOT / "data" / "bc-ohs" / "code.json").read_text(encoding="utf-8")),
}


def _scene(row: int) -> Scene:
    return Scene(id="S", heading="H", day="D1", tags=[HazardTag(row=row, label="l", detail="d")], violations=[])


def test_heights_ab_has_139_must_and_152_engineer():
    reqs = route(_scene(9), "AB", CODES)
    by_section = {r.section: r for r in reqs if r.row == 9}
    assert by_section["139"].kind == "must"
    assert by_section["152"].kind == "engineer"


def test_heights_bc_has_no_139_and_has_11_2():
    reqs = route(_scene(9), "BC", CODES)
    sections = {r.section for r in reqs if r.row == 9}
    assert "139" not in sections
    assert "11.2" in sections


def test_no_tags_returns_only_welfare_ab():
    reqs = route(Scene(id="S0", heading="H", day="D1", tags=[], violations=[]), "AB", CODES)
    assert len(reqs) == 9
    assert all(r.row == 0 for r in reqs)


def test_missing_section_raises_keyerror():
    ROUTES[9]["AB"].append((9, ["999.999"]))
    try:
        with pytest.raises(KeyError):
            route(_scene(9), "AB", CODES)
    finally:
        ROUTES[9]["AB"].pop()
