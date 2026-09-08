from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Mapping


DEFAULT_GRAFANA_MCP_TOOLS = (
    "search_dashboards",
    "get_dashboard_by_uid",
    "update_dashboard",
    "create_dashboard",
    "list_datasources",
    "query_prometheus",
    "query_loki_logs",
    "create_annotation",
)


@dataclass(frozen=True)
class GrafanaMcpConfig:
    grafana_url: str
    service_account_token: str | None = None
    username: str | None = None
    password: str | None = None
    org_id: str | None = None
    extra_headers: Mapping[str, str] = field(default_factory=dict)
    command: str = "uvx"
    args: tuple[str, ...] = ("mcp-grafana",)
    tool_filter: tuple[str, ...] = DEFAULT_GRAFANA_MCP_TOOLS

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "GrafanaMcpConfig":
        source = os.environ if env is None else env
        grafana_url = source.get("GRAFANA_URL", "").strip()
        if not grafana_url:
            raise ValueError("GRAFANA_URL is required for Grafana MCP.")

        command = source.get("GRAFANA_MCP_COMMAND", "uvx").strip() or "uvx"
        args_raw = source.get("GRAFANA_MCP_ARGS", "mcp-grafana").strip()
        args = tuple(part for part in args_raw.split() if part)
        if not args:
            raise ValueError("GRAFANA_MCP_ARGS must contain at least the MCP server name or flags.")

        extra_headers_raw = source.get("GRAFANA_EXTRA_HEADERS", "").strip()
        extra_headers: Mapping[str, str] = {}
        if extra_headers_raw:
            parsed = json.loads(extra_headers_raw)
            if not isinstance(parsed, dict) or not all(
                isinstance(key, str) and isinstance(value, str)
                for key, value in parsed.items()
            ):
                raise ValueError("GRAFANA_EXTRA_HEADERS must be a JSON object of string values.")
            extra_headers = parsed

        tool_filter_raw = source.get("GRAFANA_MCP_TOOL_FILTER", "").strip()
        tool_filter = (
            tuple(part.strip() for part in tool_filter_raw.split(",") if part.strip())
            if tool_filter_raw
            else DEFAULT_GRAFANA_MCP_TOOLS
        )

        return cls(
            grafana_url=grafana_url,
            service_account_token=source.get("GRAFANA_SERVICE_ACCOUNT_TOKEN") or None,
            username=source.get("GRAFANA_USERNAME") or None,
            password=source.get("GRAFANA_PASSWORD") or None,
            org_id=source.get("GRAFANA_ORG_ID") or None,
            extra_headers=extra_headers,
            command=command,
            args=args,
            tool_filter=tool_filter,
        )

    def server_env(self) -> dict[str, str]:
        env = {"GRAFANA_URL": self.grafana_url}
        if self.service_account_token:
            env["GRAFANA_SERVICE_ACCOUNT_TOKEN"] = self.service_account_token
        if self.username:
            env["GRAFANA_USERNAME"] = self.username
        if self.password:
            env["GRAFANA_PASSWORD"] = self.password
        if self.org_id:
            env["GRAFANA_ORG_ID"] = self.org_id
        if self.extra_headers:
            env["GRAFANA_EXTRA_HEADERS"] = json.dumps(dict(self.extra_headers), sort_keys=True)
        return env

    def sanitized(self) -> dict[str, object]:
        env = {
            key: ("<set>" if key in {"GRAFANA_SERVICE_ACCOUNT_TOKEN", "GRAFANA_PASSWORD"} else value)
            for key, value in self.server_env().items()
        }
        return {
            "command": self.command,
            "args": list(self.args),
            "env": env,
            "tool_filter": list(self.tool_filter),
        }


def build_grafana_mcp_toolset(config: GrafanaMcpConfig | None = None):
    """Return an ADK McpToolset for the official grafana/mcp-grafana server."""
    cfg = config or GrafanaMcpConfig.from_env()

    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=cfg.command,
                args=list(cfg.args),
                env=cfg.server_env(),
            ),
        ),
        tool_filter=list(cfg.tool_filter),
        tool_name_prefix="grafana",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect the Grafana MCP ADK configuration.")
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Validate environment-derived config without starting Grafana or mcp-grafana.",
    )
    args = parser.parse_args()

    config = GrafanaMcpConfig.from_env()
    if args.check_config:
        print(json.dumps(config.sanitized(), indent=2, sort_keys=True))
        return

    build_grafana_mcp_toolset(config)
    print("Grafana MCP ADK toolset constructed.")


if __name__ == "__main__":
    main()
