"""Hazard row to Code section routing: ROUTES table, classify, route."""
from __future__ import annotations

import re

from agent.model import HazardTag, Requirement, Scene
from agent.query_code import blob

ROUTES: dict[int, dict[str, list[tuple[int, list[str]]]]] = {
    1: {"AB": [], "BC": []},
    2: {"AB": [(10, ["*"]), (33, ["*"])], "BC": [(21, ["*"])]},
    3: {
        "AB": [(4, ["16", "17", "21", "22"]), (29, ["*"]), (26, ["*"])],
        "BC": [(5, ["5.53", "5.97", "5.98", "5.101", "5.104"])],
    },
    4: {"AB": [(17, ["*"]), (15, ["212", "213"])], "BC": [(19, ["19.10", "19.16", "19.18"])]},
    5: {"AB": [(15, ["212", "213", "215.4"]), (25, ["*"])], "BC": [(12, ["*"]), (10, ["10.3"])]},
    6: {"AB": [(21, ["292.1", "293", "294"]), (23, ["*"]), (30, ["*"])], "BC": [(13, ["*"]), (15, ["*"])]},
    7: {"AB": [(5, ["47", "49", "52", "56"])], "BC": [(9, ["9.5", "9.9", "9.13", "9.17"])]},
    8: {"AB": [(2, ["7", "8", "9"]), (9, ["139", "140"])], "BC": [(11, ["11.2"])]},
    9: {
        "AB": [(9, ["139", "140", "152", "152.1"]), (6, ["64", "65", "106"])],
        "BC": [(11, ["11.2"]), (14, ["*"])],
    },
    10: {"AB": [(25, ["*"]), (22, ["311"]), (18, ["*"])], "BC": [(12, ["*"])]},
    11: {"AB": [(19, ["*"]), (31, ["*"])], "BC": [(16, ["*"]), (24, ["24.63"])]},
    12: {"AB": [(7, ["115", "116", "117", "118"]), (6, ["106"])], "BC": [(7, ["7.27", "7.31"]), (14, ["*"])]},
    13: {
        "AB": [(15, ["212", "213", "214", "214.1", "215", "215.1", "215.2", "215.4"])],
        "BC": [(10, ["10.3", "10.4", "10.7", "10.9", "10.10"]), (19, ["19.10", "19.16"])],
    },
}

WELFARE: dict[str, list[tuple[int, list[str]]]] = {
    "AB": [(2, ["7", "8"]), (11, ["178", "179", "181"]), (24, ["355"]), (7, ["115", "116", "117"])],
    "BC": [(3, ["3.16", "3.17", "3.18", "3.19"]), (28, ["28.10"]), (4, ["4.87"])],
}

FIREARMS_TEXT = "PAL holder or direct supervision by PAL holder; Actsafe MP-06-2024 (BC)"


def classify(text: str) -> str:
    if re.search(r"professional engineer", text, re.I):
        return "engineer"
    if re.search(r"\bpermit\b", text, re.I):
        return "permit"
    if re.search(r"competent (worker|person)|first aider|blaster|tending worker", text, re.I):
        return "competent"
    if re.search(r"must not", text, re.I):
        return "must_not"
    if re.search(r"must", text, re.I):
        return "must"
    return "must"


def _index(parts: list[dict]) -> dict[int, dict[str, dict]]:
    idx: dict[int, dict[str, dict]] = {}
    for p in parts:
        idx.setdefault(p["part"], {})
        for s in p["sections"]:
            idx[p["part"]][s["section"]] = s
    return idx


def _expand(row: int, province: str, idx: dict[int, dict[str, dict]], entries: list[tuple[int, list[str]]]) -> list[Requirement]:
    reqs: list[Requirement] = []
    for part, sections in entries:
        if part not in idx:
            raise KeyError(f"{province}:{part}:{sections}")
        part_idx = idx[part]
        sec_ids = list(part_idx.keys()) if sections == ["*"] else sections
        for sec_id in sec_ids:
            if sec_id not in part_idx:
                raise KeyError(f"{province}:{part}:{sec_id}")
            s = part_idx[sec_id]
            text = blob(s)
            if text.strip() == "Repealed.":
                continue
            reqs.append(
                Requirement(
                    row=row,
                    code=f"{province}:{sec_id}",
                    part=part,
                    section=sec_id,
                    heading=s["heading"],
                    text=text,
                    kind=classify(text),
                )
            )
    return reqs


def route(scene: Scene, province: str, codes: dict[str, list]) -> list[Requirement]:
    idx = _index(codes[province])
    reqs: list[Requirement] = []
    for row in sorted({tag.row for tag in scene.tags}):
        if row == 1:
            reqs.append(
                Requirement(
                    row=1,
                    code=f"{province}:FIREARMS",
                    part=0,
                    section="FIREARMS",
                    heading="Firearms",
                    text=FIREARMS_TEXT,
                    kind="competent",
                )
            )
            continue
        reqs.extend(_expand(row, province, idx, ROUTES[row][province]))
    reqs.extend(_expand(0, province, idx, WELFARE[province]))
    reqs.sort(key=lambda r: (r.row, r.part, r.section))
    return reqs
