# Grafana MCP Integration Notes

UCS publishes significant safety results from `POST /api/analyze` through the
official `grafana/mcp-grafana` server `create_annotation` tool.

## Local transport

The default local path launches the official server over stdio:

```text
GRAFANA_URL=http://localhost:3000
GRAFANA_USERNAME=admin
GRAFANA_PASSWORD=<local-password>
GRAFANA_MCP_COMMAND=uvx
GRAFANA_MCP_ARGS=mcp-grafana
```

The client checks that `create_annotation` exists, sends severity, hazard labels,
and required clears, parses the annotation ID, and returns a receipt. `GREEN`
results are not published to avoid annotation noise.

## Hosted transport

For Vercel, host the official server separately using Streamable HTTP and configure
these server-side variables:

```text
GRAFANA_MCP_URL=https://<hosted-mcp-service>/mcp
GRAFANA_MCP_SERVER_TOKEN=<optional-mcp-caller-token>
GRAFANA_PUBLIC_URL=https://<grafana-host>
GRAFANA_MCP_TIMEOUT_SECONDS=20
```

The hosted server owns the Grafana connection credentials. The Vercel function
only calls the MCP endpoint and never sends credentials to the browser. Hosted MCP
is implemented and unit-tested, but is not claimed as live until a real endpoint
returns an annotation receipt.

## Safety boundary

Grafana publication is an observability side effect. It cannot override or change
the deterministic Python safety result. Gemini structured extraction and Grafana
publication must be described separately in demos and submission copy.
