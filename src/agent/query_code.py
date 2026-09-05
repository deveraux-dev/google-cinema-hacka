"""Search both extracted Codes: query_code.py <regex> [--full]."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODES = {
    "AB": ROOT / "data" / "alberta-ohs" / "code.json",
    "BC": ROOT / "data" / "bc-ohs" / "code.json",
}


def blob(section: dict) -> str:
    parts = [t["text"] for t in section["text"]]
    parts += [c["text"] for c in section.get("clauses", [])]
    return " ".join(parts)


def search(pattern: str):
    rx = re.compile(pattern, re.I)
    for label, path in CODES.items():
        for part in json.loads(path.read_text(encoding="utf-8")):
            for s in part["sections"]:
                text = blob(s)
                if rx.search(text) or rx.search(s["heading"]):
                    yield label, part["part"], s["section"], s["heading"], text


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: query_code.py <regex> [--full]")
    full = "--full" in sys.argv
    n = 0
    for label, part, sec, heading, text in search(sys.argv[1]):
        n += 1
        body = text if full else text[:240]
        print(f"{label} P{part} s.{sec} [{heading}] :: {body}")
    print(f"-- {n} sections")


if __name__ == "__main__":
    main()
