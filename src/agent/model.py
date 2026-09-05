"""Plan/scene/register data types and production.plan.json loader."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Jurisdiction:
    province: str
    municipality: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Location:
    name: str
    lat: float | None
    lon: float | None
    hospital_minutes: int | None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Day:
    day: str
    location: str
    night: bool
    exterior: bool
    build_or_strike: bool
    headcount: int
    on_call: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Roles:
    first_ad: str
    safety_officer: str
    armorer: str
    rigger: str
    first_aiders: list[str]
    catering_lead: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SitePractice:
    condor_wind_kmh: float | None
    crane_wind_kmh: float | None
    exterior_pyro_wind_kmh: float | None
    rig_recheck_hours: float | None
    ticket_preexpiry_days: int = 90

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Plan:
    production: str
    jurisdiction: Jurisdiction
    locations: list[Location]
    schedule: list[Day]
    roles: Roles
    site_practice: SitePractice
    created: str
    revised: str

    def to_dict(self) -> dict:
        return {
            "production": self.production,
            "jurisdiction": self.jurisdiction.to_dict(),
            "locations": [loc.to_dict() for loc in self.locations],
            "schedule": [day.to_dict() for day in self.schedule],
            "roles": self.roles.to_dict(),
            "site_practice": self.site_practice.to_dict(),
            "created": self.created,
            "revised": self.revised,
        }


@dataclass(frozen=True)
class HazardTag:
    row: int
    label: str
    detail: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Scene:
    id: str
    heading: str
    day: str
    tags: list[HazardTag]
    violations: list[str]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "heading": self.heading,
            "day": self.day,
            "tags": [t.to_dict() for t in self.tags],
            "violations": list(self.violations),
        }


@dataclass(frozen=True)
class Requirement:
    row: int
    code: str
    part: int
    section: str
    heading: str
    text: str
    kind: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Ticket:
    person: str
    role: str
    issuer: str
    issued: str
    expires: str
    jurisdiction: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Clear:
    scene_id: str
    section_id: str
    by: str
    role: str
    date: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Lock:
    scene_id: str
    role: str
    person: str
    section_id: str
    applied: str
    released: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


_PROVINCES = {"AB", "BC"}


def load_plan(path: str) -> Plan:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    province = raw["jurisdiction"]["province"]
    if not province:
        raise ValueError("jurisdiction required")
    if province not in _PROVINCES:
        raise ValueError("unknown province")
    jurisdiction = Jurisdiction(province=province, municipality=raw["jurisdiction"]["municipality"])
    locations = [
        Location(name=loc["name"], lat=loc["lat"], lon=loc["lon"], hospital_minutes=loc["hospital_minutes"])
        for loc in raw["locations"]
    ]
    schedule = [
        Day(
            day=d["day"],
            location=d["location"],
            night=d["night"],
            exterior=d["exterior"],
            build_or_strike=d["build_or_strike"],
            headcount=d["headcount"],
            on_call=d["on_call"],
        )
        for d in raw["schedule"]
    ]
    roles_raw = raw["roles"]
    roles = Roles(
        first_ad=roles_raw["first_ad"],
        safety_officer=roles_raw["safety_officer"],
        armorer=roles_raw["armorer"],
        rigger=roles_raw["rigger"],
        first_aiders=list(roles_raw["first_aiders"]),
        catering_lead=roles_raw["catering_lead"],
    )
    sp_raw = raw["site_practice"]
    site_practice = SitePractice(
        condor_wind_kmh=sp_raw["condor_wind_kmh"],
        crane_wind_kmh=sp_raw["crane_wind_kmh"],
        exterior_pyro_wind_kmh=sp_raw["exterior_pyro_wind_kmh"],
        rig_recheck_hours=sp_raw["rig_recheck_hours"],
        ticket_preexpiry_days=sp_raw.get("ticket_preexpiry_days", 90),
    )
    provenance = raw.get("provenance", {})
    return Plan(
        production=raw["production"],
        jurisdiction=jurisdiction,
        locations=locations,
        schedule=schedule,
        roles=roles,
        site_practice=site_practice,
        created=provenance.get("created", ""),
        revised=provenance.get("revised", ""),
    )
