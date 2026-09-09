import os
import json
import asyncio
import shlex
from contextlib import asynccontextmanager


def _failure(message: str, transport: str = "disabled") -> dict:
    return {
        "published": False,
        "annotation_id": "",
        "dashboard_url": "",
        "transport": transport,
        "error": message,
    }


@asynccontextmanager
async def _connect_mcp():
    remote_url = os.environ.get("GRAFANA_MCP_URL", "").strip()
    if remote_url:
        import httpx2
        from mcp.client.streamable_http import streamable_http_client

        headers = {}
        server_token = os.environ.get("GRAFANA_MCP_SERVER_TOKEN")
        if server_token:
            headers["Authorization"] = f"Bearer {server_token}"
        timeout = float(os.environ.get("GRAFANA_MCP_TIMEOUT_SECONDS", "20"))
        async with httpx2.AsyncClient(headers=headers, timeout=timeout) as http_client:
            async with streamable_http_client(remote_url, http_client=http_client) as streams:
                read, write, _ = streams
                yield read, write, "streamable_http"
        return

    from mcp import StdioServerParameters
    from mcp.client.stdio import stdio_client

    server_env = {
        key: value
        for key in (
            "GRAFANA_URL",
            "GRAFANA_SERVICE_ACCOUNT_TOKEN",
            "GRAFANA_API_KEY",
            "GRAFANA_USERNAME",
            "GRAFANA_PASSWORD",
            "GRAFANA_ORG_ID",
            "GRAFANA_EXTRA_HEADERS",
        )
        if (value := os.environ.get(key))
    }
    server_params = StdioServerParameters(
        command=os.environ.get("GRAFANA_MCP_COMMAND", "uvx"),
        args=shlex.split(os.environ.get("GRAFANA_MCP_ARGS", "mcp-grafana")),
        env=server_env,
    )
    async with stdio_client(server_params) as streams:
        read, write = streams
        yield read, write, "stdio"

async def publish_to_grafana(scene_id: str, severity: str, hazard_labels: list, required_clears: list) -> dict:
    """
    Connects to the official Grafana MCP server and pushes a global annotation for RED/STOP/REVIEW results.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    grafana_token = os.environ.get("GRAFANA_SERVICE_ACCOUNT_TOKEN") or os.environ.get("GRAFANA_API_KEY")
    grafana_username = os.environ.get("GRAFANA_USERNAME")
    grafana_password = os.environ.get("GRAFANA_PASSWORD")
    remote_mcp_url = os.environ.get("GRAFANA_MCP_URL")
    dashboard_url = os.environ.get("GRAFANA_PUBLIC_URL") or grafana_url or ""

    if not remote_mcp_url and (not grafana_url or not (grafana_token or (grafana_username and grafana_password))):
        return _failure(
            "Set GRAFANA_MCP_URL for hosted MCP, or GRAFANA_URL plus Grafana credentials for local stdio. Skipping Grafana publish."
        )

    try:
        from mcp import ClientSession
    except Exception as exc:
        return _failure(f"Python MCP package unavailable. Skipping Grafana publish: {exc}")
    
    if severity not in ["RED", "STOP", "REVIEW"]:
        # Only publish significant severity events to avoid spamming
        return _failure(f"Severity {severity} does not require a Grafana annotation.")

    # Format the annotation text
    labels_str = ", ".join(hazard_labels) if hazard_labels else "None"
    clears_str = ", ".join(required_clears) if required_clears else "None"
    
    annotation_text = (
        f"**UCS Incident**\n"
        f"Scene: {scene_id}\n"
        f"Severity: **{severity}**\n"
        f"Hazards: {labels_str}\n"
        f"Required Clears: {clears_str}"
    )
    
    tags = ["ucs", f"scene:{scene_id}", f"severity:{severity}"] + [f"hazard:{l}" for l in hazard_labels]

    try:
        timeout = float(os.environ.get("GRAFANA_MCP_TIMEOUT_SECONDS", "20"))
        async with asyncio.timeout(timeout):
            async with _connect_mcp() as (read, write, transport):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    tools_response = await session.list_tools()
                    available_tools = [tool.name for tool in tools_response.tools]
                    tool_name = next(
                        (
                            name
                            for name in available_tools
                            if "annotation" in name.lower() and "create" in name.lower()
                        ),
                        "create_annotation",
                    )
                    if tool_name not in available_tools:
                        return _failure(
                            "Official Grafana MCP server did not expose create_annotation.",
                            transport,
                        )

                    result = await session.call_tool(
                        tool_name,
                        arguments={"text": annotation_text, "tags": tags},
                    )
                    if getattr(result, "is_error", False):
                        return _failure(
                            f"MCP Tool Error: {str(result.content)[:300]}",
                            transport,
                        )

                    output_content = str(result.content)
                    annotation_id = "grafana-mcp-success"
                    if result.content:
                        result_text = getattr(result.content[0], "text", "")
                        if result_text:
                            try:
                                parsed = json.loads(result_text)
                                annotation_id = str(
                                    parsed.get("Payload", {}).get("id") or annotation_id
                                )
                                output_content = result_text
                            except json.JSONDecodeError:
                                pass

                    return {
                        "published": True,
                        "annotation_id": annotation_id,
                        "dashboard_url": dashboard_url,
                        "transport": transport,
                        "receipt": output_content,
                        "error": None,
                    }

    except Exception as e:
        transport = "streamable_http" if remote_mcp_url else "stdio"
        return _failure(f"Failed to connect to Grafana MCP: {str(e)[:300]}", transport)
