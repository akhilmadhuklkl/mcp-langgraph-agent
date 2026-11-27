# MCP Multi-Server Agent

A Python AI agent that connects to multiple MCP servers, discovers their tools,
and routes multi-step tasks through a LangGraph workflow.

## What this demonstrates

- One client connecting to three independent MCP servers over stdio
- Dynamic `list_tools()` discovery and namespaced tool routing
- Human-readable tool catalog with descriptions and input schemas
- Execution traces with tool arguments, status, results, and timing
- Explicit workflow state for plans, results, errors, and approvals
- Optional LLM planner with structured tool plans
- Result-aware execution where later tools can consume earlier results
- Approval gates before mutating GitHub, Gmail, or Notion tools
- Bounded MCP retries, exponential backoff, and per-call timeouts
- SQLite persistence for run state and resumable workflows
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
python -m mcp_agent.cli run "Check GitHub issues and my Gmail inbox"
```

List recent runs:

```powershell
python -m mcp_agent.cli history
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
python -m mcp_agent.cli "Find GitHub issues and related Notion notes" --model
```

The LLM receives the discovered MCP tool catalog and must return exact
namespaced tool names plus JSON arguments. Deterministic planning remains the
default for local development and tests.

Multi-step plans can reference the latest tool output with `${last_result}`.
For example, a GitHub search can feed its result into a related Notion search.

Mutating tools are policy-protected. The graph pauses with
`approval_status="pending"` before executing tools such as
`gmail.draft_email` or `notion.create_page`.

Pending state can be resumed by applying an approval decision. An approved
state continues at the paused step; a rejected state ends safely without
calling the mutating tool.

The programmatic entry point is `resume_workflow(registry, state, approved)`.

MCP calls default to a 30-second timeout and two retries. These values can be
configured through `MCPToolRegistry(timeout_seconds=..., max_retries=...)`.

CLI runs are persisted in `data/agent_runs.db` (ignored by Git). Each run prints
a UUID that can be used by future resume and run-history commands.

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
