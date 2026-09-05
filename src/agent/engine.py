"""One engine run: route, first aid, register, locks, severity per scene."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agent.first_aid import first_aid_requirement
from agent.locks import open_hold, release, severity
from agent.model import Clear, HazardTag, Plan, Scene, Ticket, load_plan
from agent.register import check_role, load_register
from agent.routing import route

ROOT = Path(__file__).resolve().parents[2]
CODE_PATHS = {"AB": ROOT / "data" / "alberta-ohs" / "code.json", "BC": ROOT / "data" / "bc-ohs" / "code.json"}
SCHEDULES_PATH = ROOT / "data" / "alberta-ohs" / "schedules.json"

ROLE_TICKET = {"engineer": "fall_protection", "rigger": "fall_protection", "first_aider": "first_aid"}


def load_scenes(path: str) -> list[Scene]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [
        Scene(
            id=s["id"],
            heading=s["heading"],
            day=s["day"],
            tags=[HazardTag(row=t["row"], label=t["label"], detail=t["detail"]) for t in s["tags"]],
            violations=list(s["violations"]),
        )
        for s in raw
    ]


def load_clears(path: str) -> list[Clear]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [Clear(scene_id=c["scene_id"], section_id=c["section_id"], by=c["by"], role=c["role"], date=c["date"]) for c in raw]


def load_codes() -> dict[str, list]:
    return {p: json.loads(path.read_text(encoding="utf-8")) for p, path in CODE_PATHS.items()}


def load_schedules() -> list[dict]:
    return json.loads(SCHEDULES_PATH.read_text(encoding="utf-8"))


def run(plan: Plan, scenes: list[Scene], clears: list[Clear], register: list[Ticket], today: str, codes: dict[str, list], schedules: list[dict]) -> dict:
    province = plan.jurisdiction.province
    preexpiry_days = plan.site_practice.ticket_preexpiry_days
    state: dict = {}
    out_scenes = []
    for scene in scenes:
        requirements = route(scene, province, codes)
        open_hold(state, scene.id, requirements, plan.roles)
        for clear in clears:
            if clear.scene_id == scene.id:
                release(state, scene.id, clear.role, clear.by, clear.section_id, clear.date)
        day = next(d for d in plan.schedule if d.day == scene.day)
        location = next(loc for loc in plan.locations if loc.name == day.location)
        schedules_arg = schedules if province == "AB" else None
        fa = first_aid_requirement(day, scene.tags, location.hospital_minutes, schedules_arg)
        register_status: dict[str, str] = {}
        for lock in state[scene.id]["locks"]:
            if lock.role in ROLE_TICKET and lock.role not in register_status:
                register_status[lock.role] = check_role(register, ROLE_TICKET[lock.role], province, today, preexpiry_days)
        sev = severity(state, scene.id, requirements, register_status, violations=tuple(scene.violations))
        out_scenes.append(
            {
                "id": scene.id,
                "heading": scene.heading,
                "day": scene.day,
                "severity": sev,
                "requirements": [r.to_dict() for r in requirements],
                "locks": [lock.to_dict() for lock in state[scene.id]["locks"]],
                "first_aid": fa,
                "register": register_status,
            }
        )
    return {"production": plan.production, "jurisdiction": province, "today": today, "scenes": out_scenes}


def replay(plan_path: str, scenes_path: str, clears_path: str, register_path: str, today: str) -> str:
    codes = load_codes()
    schedules = load_schedules()

    def once() -> str:
        plan = load_plan(plan_path)
        scenes = load_scenes(scenes_path)
        clears = load_clears(clears_path)
        register = load_register(register_path)
        result = run(plan, scenes, clears, register, today, codes, schedules)
        return json.dumps(result, sort_keys=True, ensure_ascii=False)

    a, b = once(), once()
    if a != b:
        raise AssertionError("non-deterministic")
    return a


def main() -> None:
    plan_path, scenes_path, clears_path, register_path, today = sys.argv[1:6]
    print(replay(plan_path, scenes_path, clears_path, register_path, today))


if __name__ == "__main__":
    main()
