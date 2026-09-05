"""Alberta OHS Code schedule tables (King's Printer HTML) -> data/alberta-ohs/schedules.json."""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "alberta-ohs" / "OHSCode_AR191-2021_KingsPrinter_current.html"
OUT = ROOT / "data" / "alberta-ohs" / "schedules.json"

TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")
SCHED = re.compile(r"<p class=(?:Heading|PartTitle)[^>]*>(?:(?!</p>).)*?Schedule\s*<span\s*class=SectionNumber>(\d+)</span>(?:(?!</p>).)*?</p>", re.S)
TABLE_HEAD = re.compile(r"<p class=Heading[^>]*>(?:(?!</p>).)*?Table (\d+)\s*<br>\s*(.*?)</p>", re.S)
SEE = re.compile(r"\[\s*See\s+(.*?)\]", re.S)
TABLE = re.compile(r"<table[^>]*>(.*?)</table>", re.S)
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)


def _text(s: str) -> str:
    s = re.sub(r"</p>", " | ", s)
    return WS.sub(" ", html.unescape(TAG.sub("", s))).replace("‑", "-").strip(" |")


def parse(src: Path = SRC) -> list[dict]:
    body = src.read_text(encoding="utf-8", errors="replace")
    marks = [(m.start(), int(m.group(1))) for m in SCHED.finditer(body)]
    out: list[dict] = []
    for i, (start, sched) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        chunk = body[start:end]
        for th in TABLE_HEAD.finditer(chunk):
            after = chunk[th.end():]
            see = SEE.search(after[:600])
            tbl = TABLE.search(after)
            if not tbl or tbl.start() > 4000:
                continue
            rows = []
            for r in ROW.finditer(tbl.group(1)):
                cells = [_text(c) for c in CELL.findall(r.group(1))]
                if any(cells):
                    rows.append(cells)
            out.append({
                "schedule": sched,
                "table": int(th.group(1)),
                "title": _text(th.group(2)),
                "see": _text(see.group(1)) if see else None,
                "rows": rows,
            })
    return out


def main() -> None:
    tables = parse()
    OUT.write_text(json.dumps(tables, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"tables={len(tables)} -> {OUT.relative_to(ROOT)}")
    if len(sys.argv) > 2:
        s, t = int(sys.argv[1]), int(sys.argv[2])
        for tb in tables:
            if tb["schedule"] == s and tb["table"] == t:
                print(json.dumps(tb, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
