"""Local HTTP harness: serves engine.run() JSON for the front end to fetch."""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from agent.engine import load_clears, load_codes, load_register, load_schedules, load_scenes, run
from agent.model import load_plan

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLES = {
    "plan": ROOT / "samples" / "production.plan.json",
    "scenes": ROOT / "samples" / "scenes.json",
    "clears": ROOT / "samples" / "clears.json",
    "register": ROOT / "samples" / "crew.csv",
}


def _run(paths: dict[str, Path], today: str) -> dict:
    plan = load_plan(str(paths["plan"]))
    scenes = load_scenes(str(paths["scenes"]))
    clears = load_clears(str(paths["clears"]))
    register = load_register(str(paths["register"]))
    return run(plan, scenes, clears, register, today, load_codes(), load_schedules())


def make_handler(paths: dict[str, Path], today: str) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path not in ("/", "/engine.json"):
                self.send_response(404)
                self.end_headers()
                return
            try:
                body = json.dumps(_run(paths, today), sort_keys=True, ensure_ascii=False).encode("utf-8")
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args) -> None:
            print(f"harness: {self.address_string()} {fmt % args}")

    return Handler


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    today = sys.argv[2] if len(sys.argv) > 2 else "2026-09-05"
    server = HTTPServer(("127.0.0.1", port), make_handler(DEFAULT_SAMPLES, today))
    print(f"harness serving GET /engine.json on http://127.0.0.1:{port} (today={today})")
    server.serve_forever()


if __name__ == "__main__":
    main()
