"""Schedule 2 first aid lookup: hazard class, travel band, headcount band."""
from __future__ import annotations

import re

from agent.model import Day, HazardTag

_BAND_COLUMN = {"close": 1, "distant": 2, "isolated": 3}
_TABLE_BY_CLASS = {"medium": 6, "high": 7}


def hazard_class(day: Day, scene_tags: list[HazardTag]) -> str:
    if day.build_or_strike or any(tag.row == 2 for tag in scene_tags):
        return "high"
    return "medium"


def travel_band(minutes: int) -> str:
    if minutes <= 20:
        return "close"
    if minutes <= 40:
        return "distant"
    return "isolated"


def headcount_band(n: int, table_rows: list[list[str]]) -> list[str]:
    for row in table_rows:
        label = row[0]
        if "or more" in label:
            low = int(re.search(r"\d+", label).group())
            if n >= low:
                return row
        elif "–" in label:
            lo, hi = (int(x.strip()) for x in label.split("–"))
            if lo <= n <= hi:
                return row
        elif n == int(label):
            return row
    raise ValueError(f"no headcount band for {n}")


def _table(schedules: list[dict], table_num: int) -> dict:
    for t in schedules:
        if t["schedule"] == 2 and t["table"] == table_num:
            return t
    raise KeyError(f"schedule 2 table {table_num}")


def first_aid_requirement(day: Day, tags: list[HazardTag], hospital_minutes: int, schedules: list[dict] | None) -> dict:
    if not schedules:
        return {"table": "3-A", "requirement": "Schedule 3-A not yet extracted", "unresolved": True}
    cls = hazard_class(day, tags)
    table_num = _TABLE_BY_CLASS[cls]
    band = travel_band(hospital_minutes)
    table = _table(schedules, table_num)
    row = headcount_band(day.headcount, table["rows"][1:])
    return {
        "table": table_num,
        "class": cls,
        "band": band,
        "headcount_row": row[0],
        "requirement": row[_BAND_COLUMN[band]],
    }
