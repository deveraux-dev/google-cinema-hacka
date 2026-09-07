"""Grafana access via the official mcp-grafana server (stdio). Track rule: Grafana through MCP."""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

MCP_EXE = ROOT / ".tools" / "mcp-grafana" / "mcp-grafana.exe"


def _params() -> StdioServerParameters:
    return StdioServerParameters(
        command=str(MCP_EXE),
        args=[],
        env={
            **os.environ,
            "GRAFANA_URL": os.environ["GRAFANA_URL"],
            "GRAFANA_SERVICE_ACCOUNT_TOKEN": os.environ["GRAFANA_SERVICE_ACCOUNT_TOKEN"],
        },
    )


async def list_tools() -> list[dict]:
    async with stdio_client(_params()) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.list_tools()
            return [{"name": t.name, "schema": t.input_schema} for t in res.tools]


async def call(name: str, args: dict) -> str:
    async with stdio_client(_params()) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool(name, args)
            return "\n".join(c.text for c in res.content if getattr(c, "text", None))


async def call_many(calls: list[tuple[str, dict]]) -> list[str]:
    out: list[str] = []
    async with stdio_client(_params()) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            for name, args in calls:
                res = await s.call_tool(name, args)
                out.append("\n".join(c.text for c in res.content if getattr(c, "text", None)))
    return out


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    if mode == "list":
        tools = asyncio.run(list_tools())
        print(f"tools: {len(tools)}")
        for t in tools:
            print(t["name"])
    elif mode == "schema":
        want = sys.argv[2]
        for t in asyncio.run(list_tools()):
            if t["name"] == want:
                print(json.dumps(t["schema"], indent=1))
    elif mode == "call":
        print(asyncio.run(call(sys.argv[2], json.loads(sys.argv[3]))))
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
