"""Certification register: ticket loading and status/expiry ladder."""
from __future__ import annotations

import csv
from datetime import date, timedelta

from agent.model import Ticket

VALIDITY_YEARS: dict[tuple[str, str], int] = {
    ("fall_protection", "AB"): 3,
    ("fall_protection", "BC"): 3,
    ("first_aid", "AB"): 3,
    ("first_aid", "BC"): 3,
    ("mobile_equipment", "AB"): 3,
    ("mobile_equipment", "BC"): 3,
    ("blaster", "BC"): 5,
    ("pal", "*"): 5,
    ("ncso", "AB"): 3,
}

_STATUS_ORDER = {"foreign": 0, "expired": 1, "near_expiry": 2, "live": 3}


def load_register(csv_path: str) -> list[Ticket]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            Ticket(
                person=row["person"],
                role=row["role"],
                issuer=row["issuer"],
                issued=row["issued"],
                expires=row["expires"],
                jurisdiction=row["jurisdiction"],
            )
            for row in reader
        ]


def _add_years(iso_date: str, years: int) -> str:
    d = date.fromisoformat(iso_date)
    try:
        return d.replace(year=d.year + years).isoformat()
    except ValueError:
        return d.replace(month=2, day=28, year=d.year + years).isoformat()


def status(ticket: Ticket, today: str, preexpiry_days: int, province: str) -> str:
    if ticket.jurisdiction not in {province, "*", "federal"}:
        return "foreign"
    years = VALIDITY_YEARS.get((ticket.role, province), VALIDITY_YEARS.get((ticket.role, "*")))
    effective_expiry = min(ticket.expires, _add_years(ticket.issued, years)) if years is not None else ticket.expires
    if today > effective_expiry:
        return "expired"
    warn_by = (date.fromisoformat(today) + timedelta(days=preexpiry_days)).isoformat()
    if warn_by >= effective_expiry:
        return "near_expiry"
    return "live"


def check_role(register: list[Ticket], role: str, province: str, today: str, preexpiry_days: int) -> str:
    tickets = [t for t in register if t.role == role]
    if not tickets:
        return "missing"
    return min((status(t, today, preexpiry_days, province) for t in tickets), key=lambda s: _STATUS_ORDER[s])
