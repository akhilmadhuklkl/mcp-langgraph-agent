# MCP Multi-Server Agent

[![CI](https://github.com/akhilmadhuklkl/mcp-langgraph-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/akhilmadhuklkl/mcp-langgraph-agent/actions/workflows/ci.yml)

A Python AI agent that connects to multiple MCP servers, discovers their tools,
and routes multi-step tasks through a LangGraph workflow.

See the [architecture guide](docs/architecture.md) for the system design.
See the [security policy](SECURITY.md) for credential-handling and reporting guidance.
See [CONTRIBUTING.md](CONTRIBUTING.md) for development and pull-request guidelines.
See [CHANGELOG.md](CHANGELOG.md) for the project history.

## What this demonstrates

- One client connecting to three independent MCP servers over stdio
- Dynamic `list_tools()` discovery and namespaced tool routing
- Human-readable tool catalog with descriptions and input schemas
- Execution traces with tool arguments, status, results, and timing
- Explicit workflow state for plans, results, errors, and approvals
- Optional LLM planner with structured tool plans
- Result-aware execution where later tools can consume earlier results
- Approval gates before mutating GitHub, Gmail, or Google Drive tools
- Bounded MCP retries, exponential backoff, and per-call timeouts
- SQLite persistence for run state and resumable workflows
- Optional connection to the official GitHub MCP server over stdio
- LangGraph state-machine orchestration
- Multi-step plans such as: "Check GitHub issues and summarize related Drive documents"
- Deterministic demo mode that does not require an API key
- Optional OpenAI-backed planning and tool selection
- Explicit tool-call trace for debugging and portfolio demos
- Automated CI across Python 3.11, 3.12, and 3.13 with Ruff, pip-audit, and coverage checks

## Included MCP servers

- `github`: search issues and inspect pull requests
- `gmail`: search email and create drafts without sending
- `drive`: search project files and create documents

## Setup

```powershell
cd mcp-langgraph-agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Run the deterministic demo:

```powershell
python -m mcp_agent.cli run "Check GitHub issues and my Gmail inbox"
```

List recent runs:

```powershell
python -m mcp_agent.cli history
```

Check external MCP readiness without exposing credentials:

```powershell
python -m mcp_agent.cli doctor
```

Discover the exact tools exposed by the configured MCP servers:

```powershell
python -m mcp_agent.cli catalog
```

Preview a deterministic plan without connecting to any server:

```powershell
python -m mcp_agent.cli plan "Search Gmail for MCP and find matching Drive files"
```

Gmail and Google Drive follow the same pattern as GitHub. Set
`GMAIL_MCP_COMMAND` or `GOOGLE_DRIVE_MCP_COMMAND` and optionally the matching
`*_ARGS` variable to connect external servers. If unset, local mock servers are
used. Keep OAuth credentials in the external servers' environments and never
commit them.

For the Google-hosted MCP servers, use the included wrapper after setting
`GOOGLE_OAUTH_CLIENT_JSON` to the downloaded client JSON path:

```powershell
$env:GOOGLE_OAUTH_CLIENT_JSON = "C:\Users\User\Downloads\client_secret_<client-id>.json"
$env:GMAIL_MCP_COMMAND = "powershell"
$env:GMAIL_MCP_ARGS = "-ExecutionPolicy Bypass -File scripts\run-google-mcp.ps1 https://gmailmcp.googleapis.com/mcp/v1"
$env:GOOGLE_DRIVE_MCP_COMMAND = "powershell"
$env:GOOGLE_DRIVE_MCP_ARGS = "-ExecutionPolicy Bypass -File scripts\run-google-mcp.ps1 https://drivemcp.googleapis.com/mcp/v1"
```

Resume a pending run after a human decision:

```powershell
python -m mcp_agent.cli resume RUN_ID --approve
python -m mcp_agent.cli resume RUN_ID --reject
```

Use the model-backed planner when the optional dependency and `OPENAI_API_KEY`
are configured:

```powershell
pip install -e ".[model]"
python -m mcp_agent.cli run "Find GitHub issues and related Drive documents" --model
```

The LLM receives the discovered MCP tool catalog and must return exact
namespaced tool names plus JSON arguments. Deterministic planning remains the
default for local development and tests.

Multi-step plans can reference the latest tool output with `${last_result}`.
For example, a GitHub search can feed its result into a related Drive search.

Mutating tools are policy-protected. The graph pauses with
`approval_status="pending"` before executing tools such as
`gmail.draft_email` or `drive.create_file`.

Pending state can be resumed by applying an approval decision. An approved
state continues at the paused step; a rejected state ends safely without
calling the mutating tool.

The programmatic entry point is `resume_workflow(registry, state, approved)`.

MCP calls default to a 30-second timeout and two retries. These values can be
configured through `MCPToolRegistry(timeout_seconds=..., max_retries=...)`.

CLI runs are persisted in `data/agent_runs.db` (ignored by Git). Each run prints
a UUID that can be used by future resume and run-history commands.

To use the official GitHub MCP server with Docker, copy `.env.example` to your
environment configuration and provide `GITHUB_PERSONAL_ACCESS_TOKEN` through
your shell or environment manager. The included Docker command uses the public
`ghcr.io/github/github-mcp-server` image. Alternatively, install the native
`github-mcp-server` binary and set `GITHUB_MCP_COMMAND=github-mcp-server` with
`GITHUB_MCP_ARGS=stdio`. If the command is unset, the local mock GitHub server
is used.

On PowerShell, configure the token for the current session without putting it
in source control:

```powershell
$env:GITHUB_PERSONAL_ACCESS_TOKEN = "<your-token>"
```

For a reusable live run, authenticate GitHub with `gh auth login`, then use the
helper below. It reads the Google OAuth client path you provide and keeps all
credentials in the current process environment:

```powershell
.\scripts\run-live-agent.ps1 `
  -Request "Search Gmail for MCP and find matching Drive files" `
  -GoogleOAuthClientJson "C:\Users\User\Downloads\client_secret_<client-id>.json"
```

To run read-only contract checks against all three real MCP servers after they
are configured, use:

```powershell
python scripts/verify_live_servers.py
```

This validates that the expected tools are discoverable and accepts the same
arguments used by the agent. It is intentionally opt-in and is not part of CI
because it requires your external credentials.

For integrations that need machine-readable discovery data, use:

```powershell
python -m mcp_agent.cli catalog --json
```

Preview a deterministic plan as JSON with:

```powershell
python -m mcp_agent.cli plan "Search Gmail for MCP" --json
```

Check integration readiness as JSON with:

```powershell
python -m mcp_agent.cli doctor --json
```

Run a workflow and receive its answer, trace, metrics, and run ID as JSON with:

```powershell
python -m mcp_agent.cli run "Search Gmail for MCP" --json
```

Resume an approved or rejected pending run as JSON with:

```powershell
python -m mcp_agent.cli resume <run-id> --approve --json
```

List persisted runs as JSON with:

```powershell
python -m mcp_agent.cli history --json
```

Aggregate metrics across persisted runs with:

```powershell
python -m mcp_agent.cli metrics --json
```

Export the same report for spreadsheets with:

```powershell
python -m mcp_agent.cli metrics --csv
```

Create a standalone browser report with:

```powershell
python -m mcp_agent.cli metrics --html > metrics.html
```

Run tests:

```powershell
pytest
```

For model-backed planning, set `OPENAI_API_KEY` and run:

```powershell
python -m mcp_agent.cli "What should I do before my next meeting?" --model
```

## Architecture

```text
User request
    |
    v
LangGraph planner ----> MCP tool registry
    |                         |
    |                  GitHub / Gmail / Google Drive
    v                         |
Tool execution <-------------+
    |
    v
Final response + trace
```

The project intentionally keeps server processes separate from the client. This
makes the MCP boundary visible and makes it easy to replace the demo servers with
real services later.

The registry also supports MCP servers using Streamable HTTP. From Python, pass
the server name and endpoint URL:

```python
registry = MCPToolRegistry()
await registry.connect_streamable_http("remote", "https://example.com/mcp")
```

The discovered tools use the same `server.tool` namespace and follow the same
validation, retry, timeout, tracing, approval, and metrics behavior as stdio
servers.

To make an HTTP server available automatically to the CLI, set
`MCP_HTTP_SERVER_NAME` and `MCP_HTTP_SERVER_URL` in the environment.

## Completed engineering extensions

- Approval before mutating tools, with resumable decisions.
- SQLite persistence for graph runs and history.
- Tool-level latency, retry, and failure metrics.
- Read-only contract checks against real external MCP servers.
- Optional Streamable HTTP MCP transport.

## Possible future extensions

- Add a fourth production MCP server through the Streamable HTTP transport.
- Add dashboard export for the collected tool metrics.
- Add scheduled or event-triggered agent runs.
