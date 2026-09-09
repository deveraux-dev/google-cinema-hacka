import json
import asyncio
import sys
from contextlib import asynccontextmanager
from types import SimpleNamespace

from engine import grafana_client


def test_hosted_mcp_transport_returns_real_receipt_shape(monkeypatch):
    monkeypatch.setenv("GRAFANA_MCP_URL", "https://mcp.example.test/mcp")
    monkeypatch.setenv("GRAFANA_PUBLIC_URL", "https://grafana.example.test")

    @asynccontextmanager
    async def fake_connect():
        yield object(), object(), "streamable_http"

    class FakeSession:
        def __init__(self, read, write):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def initialize(self):
            return None

        async def list_tools(self):
            return SimpleNamespace(tools=[SimpleNamespace(name="create_annotation")])

        async def call_tool(self, name, arguments):
            assert name == "create_annotation"
            assert "severity:RED" in arguments["tags"]
            receipt = json.dumps({"Payload": {"id": 42, "message": "Annotation added"}})
            return SimpleNamespace(is_error=False, content=[SimpleNamespace(text=receipt)])

    monkeypatch.setattr(grafana_client, "_connect_mcp", fake_connect)
    monkeypatch.setitem(sys.modules, "mcp", SimpleNamespace(ClientSession=FakeSession))

    result = asyncio.run(
        grafana_client.publish_to_grafana(
            "S1", "RED", ["pyro"], ["SPFX Lead Clear"]
        )
    )

    assert result["published"] is True
    assert result["annotation_id"] == "42"
    assert result["transport"] == "streamable_http"
    assert result["dashboard_url"] == "https://grafana.example.test"
