"""Hold/lock/verify/group state machine and severity ladder."""
from __future__ import annotations

from agent.model import Lock, Requirement, Roles

_COMPETENT_ROLE_BY_ROW = {1: "armorer", 9: "rigger", 11: "first_aider"}


def _role_and_person(req: Requirement, roles: Roles) -> tuple[str, str]:
    if req.kind == "engineer":
        return "engineer", roles.rigger or ""
    if req.kind == "permit":
        return "safety_officer", roles.safety_officer or ""
    if req.kind == "competent":
        role = _COMPETENT_ROLE_BY_ROW.get(req.row, "competent")
        if role == "first_aider":
            return role, roles.first_aiders[0] if roles.first_aiders else ""
        return role, getattr(roles, role, "") or ""
    return "first_ad", roles.first_ad or ""


def open_hold(state: dict, scene_id: str, requirements: list[Requirement], roles: Roles) -> None:
    locks = []
    for req in requirements:
        role, person = _role_and_person(req, roles)
        locks.append(Lock(scene_id=scene_id, role=role, person=person, section_id=req.section, applied="", released=None))
    state[scene_id] = {"hold": True, "locks": locks, "last_released_by": None, "verified_by": None}


def release(state: dict, scene_id: str, role: str, person: str, section_id: str, date: str) -> None:
    entry = state[scene_id]
    for lock in entry["locks"]:
        if lock.role == role and lock.section_id == section_id and lock.released is None:
            if role == "on_call" and any(l.released is None for l in entry["locks"] if l is not lock):
                raise PermissionError("group lock cannot release while a personal lock remains")
            if lock.person != person:
                raise PermissionError(f"{person} may not release {role} lock owned by {lock.person}")
            lock.released = date
            entry["last_released_by"] = person
            return
    raise KeyError(f"no open lock for {role}:{section_id}")


def verify(state: dict, scene_id: str, by: str) -> bool:
    entry = state[scene_id]
    if any(lock.released is None for lock in entry["locks"]):
        return False
    if by == entry["last_released_by"]:
        return False
    entry["hold"] = False
    entry["verified_by"] = by
    return True


def group_lock(state: dict, scene_id: str, coordinator: str) -> None:
    entry = state[scene_id]
    entry["locks"].append(Lock(scene_id=scene_id, role="on_call", person=coordinator, section_id="GROUP", applied="", released=None))


def severity(state: dict, scene_id: str, requirements: list[Requirement], register_status: dict[str, str], violations: tuple[str, ...] = ()) -> str:
    entry = state[scene_id]
    kind_by_section = {req.section: req.kind for req in requirements}
    unreleased_kinds = {kind_by_section.get(lock.section_id) for lock in entry["locks"] if lock.released is None}
    if violations or "must_not" in unreleased_kinds:
        return "STOP"
    if unreleased_kinds & {"engineer", "permit", "competent"}:
        return "RED"
    if any(v in {"missing", "expired", "foreign"} for v in register_status.values()):
        return "RED"
    if "must" in unreleased_kinds:
        return "AMBER"
    if any(v == "near_expiry" for v in register_status.values()):
        return "AMBER"
    return "GREEN"
