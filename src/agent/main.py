"""End-to-end run: engine → Grafana publish → Gemini crew brief (skipped without GEMINI_API_KEY)."""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time

from agent.harness import DEFAULT_SAMPLES, _run
from agent.publish import open_locks, publish


def brief_prompt(out: dict) -> str:
    lines = [f"{s['id']} {s['severity']} {s['heading']} open_locks={len(open_locks(s))}" for s in out["scenes"]]
    return (
        "You are the 1st AD's assistant. Severity per scene was decided by the safety rules, not by you; "
        "do not change it. Write a 3-sentence crew call brief in plain English from:\n" + "\n".join(lines)
    )


def main() -> None:
    today = sys.argv[1] if len(sys.argv) > 1 else "2026-09-05"
    out = _run(DEFAULT_SAMPLES, today)
    run_id = time.strftime("%Y%m%dT%H%M%S")
    result: dict = {"run_id": run_id, "scenes": {s["id"]: s["severity"] for s in out["scenes"]}}
    result["grafana"] = asyncio.run(publish(out, run_id))
    if os.environ.get("GEMINI_API_KEY"):
        from agent.gemini_client import call_gemini

        result["gemini_brief"] = call_gemini(brief_prompt(out))
    else:
        result["gemini_brief"] = None
        print("GEMINI_API_KEY missing: brief skipped, wall still published", file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
