"""Tests for agent.register status ladder and check_role."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent.model import Ticket
from agent.register import check_role, status


def _ticket(issued: str, expires: str = "2027-01-01", jurisdiction: str = "AB", role: str = "fall_protection") -> Ticket:
    return Ticket(person="P", role=role, issuer="X", issued=issued, expires=expires, jurisdiction=jurisdiction)


def test_expired_when_validity_years_shorter_than_expires():
    assert status(_ticket("2022-01-01"), "2026-09-04", 90, "AB") == "expired"


def test_live_when_within_validity_and_outside_preexpiry():
    assert status(_ticket("2024-06-01"), "2026-09-04", 90, "AB") == "live"


def test_near_expiry_inside_preexpiry_window():
    assert status(_ticket("2024-06-01"), "2026-10-15", 90, "AB") == "near_expiry"


def test_foreign_jurisdiction():
    assert status(_ticket("2024-06-01", jurisdiction="CA"), "2026-09-04", 90, "AB") == "foreign"


def test_check_role_missing_when_no_ticket():
    assert check_role([], "fall_protection", "AB", "2026-09-04", 90) == "missing"


def test_check_role_worst_of_several_tickets():
    register = [_ticket("2024-06-01"), _ticket("2022-01-01")]
    assert check_role(register, "fall_protection", "AB", "2026-09-04", 90) == "expired"
