# MCP Multi-Server Agent

A Python AI agent that connects to multiple MCP servers, discovers their tools,
and routes multi-step tasks through a LangGraph workflow.

## What this demonstrates

- One client connecting to three independent MCP servers over stdio
- Dynamic `list_tools()` discovery and namespaced tool routing
- Human-readable tool catalog with descriptions and input schemas
- LangGraph state-machine orchestration
- Multi-step plans such as: "Check GitHub issues and summarize related Notion notes"
- Deterministic demo mode that does not require an API key
- Optional OpenAI-backed planning and tool selection
- Explicit tool-call trace for debugging and portfolio demos

## Included MCP servers

- `github`: search issues and inspect pull requests
- `gmail`: search email and create drafts without sending
- `notion`: search project pages and create notes

## Setup

```powershell
cd mcp-langgraph-agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Run the deterministic demo:

```powershell
python -m mcp_agent.cli "Check GitHub issues and my Gmail inbox"
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
    |                  GitHub / Gmail / Notion
    v                         |
Tool execution <-------------+
    |
    v
Final response + trace
```

The project intentionally keeps server processes separate from the client. This
makes the MCP boundary visible and makes it easy to replace the demo servers with
real services later.

## Suggested extensions

1. Add approval before mutating tools such as `create_task`.
2. Add a fourth server using Streamable HTTP.
3. Persist graph checkpoints in SQLite.
4. Add tool-level latency and failure metrics.
5. Add contract tests against real external MCP servers.
