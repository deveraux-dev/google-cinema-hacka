import json

import pytest

from agent.grafana_mcp import (
    DEFAULT_GRAFANA_MCP_TOOLS,
    GrafanaMcpConfig,
    build_grafana_mcp_toolset,
)


def test_config_from_env_defaults_to_official_uvx_server():
    config = GrafanaMcpConfig.from_env(
        {
            "GRAFANA_URL": "http://localhost:3000",
            "GRAFANA_SERVICE_ACCOUNT_TOKEN": "secret-token",
        }
    )

    assert config.command == "uvx"
    assert config.args == ("mcp-grafana",)
    assert config.server_env() == {
        "GRAFANA_URL": "http://localhost:3000",
        "GRAFANA_SERVICE_ACCOUNT_TOKEN": "secret-token",
    }
    assert config.tool_filter == DEFAULT_GRAFANA_MCP_TOOLS


def test_config_supports_native_binary_and_extra_headers():
    config = GrafanaMcpConfig.from_env(
        {
            "GRAFANA_URL": "https://show.grafana.net",
            "GRAFANA_MCP_COMMAND": "mcp-grafana.exe",
            "GRAFANA_MCP_ARGS": "-t stdio",
            "GRAFANA_ORG_ID": "2",
            "GRAFANA_EXTRA_HEADERS": json.dumps({"X-Production": "UCS"}),
            "GRAFANA_MCP_TOOL_FILTER": "create_annotation, update_dashboard",
        }
    )

    assert config.command == "mcp-grafana.exe"
    assert config.args == ("-t", "stdio")
    assert config.server_env()["GRAFANA_ORG_ID"] == "2"
    assert config.server_env()["GRAFANA_EXTRA_HEADERS"] == '{"X-Production": "UCS"}'
    assert config.tool_filter == ("create_annotation", "update_dashboard")


def test_config_rejects_missing_grafana_url():
    with pytest.raises(ValueError, match="GRAFANA_URL"):
        GrafanaMcpConfig.from_env({})


def test_sanitized_config_does_not_print_secrets():
    config = GrafanaMcpConfig.from_env(
        {
            "GRAFANA_URL": "http://localhost:3000",
            "GRAFANA_SERVICE_ACCOUNT_TOKEN": "secret-token",
            "GRAFANA_PASSWORD": "secret-password",
        }
    )

    sanitized = config.sanitized()

    assert sanitized["env"]["GRAFANA_SERVICE_ACCOUNT_TOKEN"] == "<set>"
    assert sanitized["env"]["GRAFANA_PASSWORD"] == "<set>"
    assert "secret-token" not in json.dumps(sanitized)
    assert "secret-password" not in json.dumps(sanitized)


def test_build_toolset_uses_google_adk_mcp_toolset(monkeypatch):
    calls = {}

    class FakeServerParameters:
        def __init__(self, **kwargs):
            calls["server_params"] = kwargs

    class FakeConnectionParams:
        def __init__(self, **kwargs):
            calls["connection_params"] = kwargs

    class FakeToolset:
        def __init__(self, **kwargs):
            calls["toolset"] = kwargs

    import types
    import sys

    monkeypatch.setitem(sys.modules, "mcp", types.SimpleNamespace(StdioServerParameters=FakeServerParameters))
    monkeypatch.setitem(sys.modules, "google", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "google.adk", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "google.adk.tools", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "google.adk.tools.mcp_tool", types.SimpleNamespace(McpToolset=FakeToolset))
    monkeypatch.setitem(
        sys.modules,
        "google.adk.tools.mcp_tool.mcp_session_manager",
        types.SimpleNamespace(StdioConnectionParams=FakeConnectionParams),
    )

    config = GrafanaMcpConfig.from_env(
        {
            "GRAFANA_URL": "http://localhost:3000",
            "GRAFANA_SERVICE_ACCOUNT_TOKEN": "secret-token",
        }
    )

    build_grafana_mcp_toolset(config)

    assert calls["server_params"] == {
        "command": "uvx",
        "args": ["mcp-grafana"],
        "env": {
            "GRAFANA_URL": "http://localhost:3000",
            "GRAFANA_SERVICE_ACCOUNT_TOKEN": "secret-token",
        },
    }
    assert calls["connection_params"]["server_params"].__class__ is FakeServerParameters
    assert calls["toolset"]["tool_filter"] == list(DEFAULT_GRAFANA_MCP_TOOLS)
    assert calls["toolset"]["tool_name_prefix"] == "grafana"
