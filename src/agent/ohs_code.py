"""Alberta OHS Code (AR 191/2021) King's Printer HTML -> data/alberta-ohs/code.json."""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "alberta-ohs" / "OHSCode_AR191-2021_KingsPrinter_current.html"
OUT = ROOT / "data" / "alberta-ohs" / "code.json"

P_TAG = re.compile(r"<p class=(\w+)[^>]*>(.*?)</p>", re.S)
TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")
SUB = re.compile(r"^\((\d+(?:\.\d+)?)\)\s*")


def _text(inner: str) -> str:
    return WS.sub(" ", html.unescape(TAG.sub("", inner))).strip()


def _secnum(inner: str) -> str | None:
    m = re.search(r"class=SectionNumber(?:new)?[^>]*>(.*?)</span>", inner, re.S)
    return _text(m.group(1)) if m else None


def parse(src: Path = SRC) -> list[dict]:
    body = src.read_text(encoding="utf-8", errors="replace")
    body = body[body.find("<p class=PartTitle") :]
    parts: list[dict] = []
    part = None
    heading = ""
    section = None
    for m in P_TAG.finditer(body):
        cls, inner = m.group(1), m.group(2)
        if cls == "PartTitle":
            t = _text(inner)
            num = re.match(r"Part (\d+)", t)
            part = {"part": int(num.group(1)) if num else None, "title": t, "sections": []}
            parts.append(part)
            continue
        if part is None:
            continue
        if cls in ("Sidenote2", "SidenoteXSB"):
            heading = _text(inner)
            continue
        if cls in ("Section", "Subsection"):
            num = _secnum(inner)
            if num is None:
                continue
            rest = _text(re.sub(r"<span class=SectionNumber(?:new)?.*?</span></span>", "", inner, count=1, flags=re.S))
            sub = SUB.match(rest)
            subnum = sub.group(1) if sub else None
            if sub:
                rest = rest[sub.end() :]
            if section is None or section["section"] != num:
                section = {"section": num, "heading": heading, "text": [], "clauses": []}
                part["sections"].append(section)
            section["text"].append({"sub": subnum, "text": rest})
            continue
        if cls in ("Clause", "Subclause") and section is not None:
            section["clauses"].append({"under": section["text"][-1]["sub"] if section["text"] else None, "text": _text(inner)})
    return parts


def main() -> None:
    parts = parse()
    OUT.write_text(json.dumps(parts, ensure_ascii=False, indent=1), encoding="utf-8")
    nsec = sum(len(p["sections"]) for p in parts)
    print(f"parts={len(parts)} sections={nsec} -> {OUT.relative_to(ROOT)}")
    if len(sys.argv) > 1:
        want = sys.argv[1]
        for p in parts:
            for s in p["sections"]:
                if s["section"] == want:
                    print(json.dumps({"part": p["part"], **s}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
