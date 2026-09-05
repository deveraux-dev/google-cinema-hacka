"""WorkSafeBC OHS Regulation (BC Reg 296/97) bclaws PDF -> data/bc-ohs/code.json."""

import json
import logging
import re
import sys
import warnings
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "bc-ohs" / "OHSR_296-97_bclaws_2026-04.pdf"
OUT = ROOT / "data" / "bc-ohs" / "code.json"

PART = re.compile(r"^Part (\d+) [–-] (.+)$")
SEC = re.compile(r"^(\d{1,2}\.\d{1,3}(?:\.\d+)?)\s+(.*)$")
SUB = re.compile(r"^\((\d+(?:\.\d+)?)\)\s*")
NOISE = re.compile(r"^(B\.C\. Reg\. 296/97|WORKERS COMPENSATION ACT|OCCUPATIONAL HEALTH AND SAFETY REGULATION|Last amended .*|\d+)$")


def _lines(reader: PdfReader):
    for page in reader.pages:
        for ln in (page.extract_text() or "").splitlines():
            ln = ln.strip()
            if ln and not NOISE.match(ln):
                yield ln


def parse(src: Path = SRC) -> list[dict]:
    logging.disable(logging.CRITICAL)
    warnings.simplefilter("ignore")
    r = PdfReader(str(src))
    if r.is_encrypted:
        r.decrypt("")
    parts: list[dict] = []
    part = None
    section = None
    heading = ""
    seen_parts: set[int] = set()
    for ln in _lines(r):
        m = PART.match(ln)
        if m and int(m.group(1)) not in seen_parts:
            n = int(m.group(1))
            seen_parts.add(n)
            part = {"part": n, "title": f"Part {n} {m.group(2).strip()}", "sections": []}
            parts.append(part)
            section = None
            continue
        if part is None:
            continue
        m = SEC.match(ln)
        if m and (section is None or _later(m.group(1), section["section"])):
            rest = m.group(2)
            sub = SUB.match(rest)
            section = {"section": m.group(1), "heading": heading, "text": [{"sub": sub.group(1) if sub else None, "text": rest[sub.end():] if sub else rest}]}
            part["sections"].append(section)
            continue
        if section is None:
            heading = ln
            continue
        sub = SUB.match(ln)
        if sub:
            section["text"].append({"sub": sub.group(1), "text": ln[sub.end():]})
        elif re.match(r"^\([a-z]+(?:\.\d+)?\)", ln):
            section["text"].append({"sub": None, "text": ln})
        elif len(ln) < 70 and not ln.endswith((".", ",", ";", "or", "and")) and ln[0].isupper():
            heading = ln
        else:
            section["text"][-1]["text"] += " " + ln
    return parts


def _later(a: str, b: str) -> bool:
    ka = [int(x) for x in a.split(".")]
    kb = [int(x) for x in b.split(".")]
    return ka > kb


def main() -> None:
    parts = parse()
    OUT.write_text(json.dumps(parts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"parts={len(parts)} sections={sum(len(p['sections']) for p in parts)} -> {OUT.relative_to(ROOT)}")
    if len(sys.argv) > 1:
        want = sys.argv[1]
        for p in parts:
            for s in p["sections"]:
                if s["section"] == want:
                    print(json.dumps({"part": p["part"], **s}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
