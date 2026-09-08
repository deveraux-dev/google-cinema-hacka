import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def publish_to_grafana(scene_id: str, severity: str, hazard_labels: list, required_clears: list) -> dict:
    """
    Connects to the official Grafana MCP server and pushes a global annotation for RED/STOP/REVIEW results.
    """
    grafana_url = os.environ.get("GRAFANA_URL")
    grafana_token = os.environ.get("GRAFANA_SERVICE_ACCOUNT_TOKEN") or os.environ.get("GRAFANA_API_KEY")

    if not grafana_url or not grafana_token:
        return {
            "published": False,
            "annotation_id": "",
            "dashboard_url": "",
            "error": "GRAFANA_URL or GRAFANA_API_KEY missing from environment. Skipping Grafana publish."
        }
    
    if severity not in ["RED", "STOP", "REVIEW"]:
        # Only publish significant severity events to avoid spamming
        return {
            "published": False,
            "annotation_id": "",
            "dashboard_url": "",
            "error": f"Severity {severity} does not require a Grafana annotation."
        }

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

    # Setup MCP Client to run `uvx mcp-grafana`
    server_params = StdioServerParameters(
        command="uvx",
        args=["mcp-grafana"],
        env={**os.environ} # pass the current env which includes GRAFANA_URL etc.
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Check available tools
                tools_response = await session.list_tools()
                available_tools = [t.name for t in tools_response.tools]
                
                # Use create_annotation tool if available (or equivalent)
                # The exact tool name depends on mcp-grafana, typically "grafana_create_annotation" or similar.
                tool_name = "create_annotation" 
                # Attempt to find the closest match if exact name differs
                for t in available_tools:
                    if "annotation" in t.lower() and "create" in t.lower():
                        tool_name = t
                        break
                
                # Create the annotation payload
                result = await session.call_tool(
                    tool_name,
                    arguments={
                        "text": annotation_text,
                        "tags": tags
                    }
                )

                if result.isError:
                    return {
                        "published": False,
                        "annotation_id": "",
                        "dashboard_url": "",
                        "error": f"MCP Tool Error: {result.content}"
                    }
                
                # Parse response for ID/URL if possible
                # If the tool just returns success text, we parse what we can
                output_content = str(result.content)
                
                return {
                    "published": True,
                    "annotation_id": "grafana-mcp-success", # Real ID would be parsed from output_content if available
                    "dashboard_url": grafana_url, # Best effort link
                    "error": None
                }
                
    except Exception as e:
        return {
            "published": False,
            "annotation_id": "",
            "dashboard_url": "",
            "error": f"Failed to connect to Grafana MCP: {str(e)}"
        }
