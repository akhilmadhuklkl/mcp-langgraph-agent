import argparse
import asyncio

from .cli_helpers import format_history
from .config import gmail_server_config, github_server_config
from .doctor import format_checks, readiness_checks
from .graph import build_graph, resume_workflow
from .mcp_client import MCPToolRegistry
from .persistence import RunStore
from .state import initial_state
from .trace import format_trace


DB_PATH = "data/agent_runs.db"


async def connect_registry() -> MCPToolRegistry:
    registry = MCPToolRegistry()
    github_config = github_server_config()
    if github_config:
        await registry.connect_external("github", github_config)
    else:
        await registry.connect(["github"])
    gmail_config = gmail_server_config()
    if gmail_config:
        await registry.connect_external("gmail", gmail_config)
    else:
        await registry.connect(["gmail"])
    await registry.connect(["notion"])
    return registry


async def run_request(request: str, planner_mode: str) -> None:
    store = RunStore()
    state = initial_state(request, planner_mode)
    run_id = store.create(request, state)
    state["run_id"] = run_id
    store.save(run_id, state)
    registry = await connect_registry()
    try:
        result = await build_graph(registry).ainvoke(state)
        store.save(run_id, result)
        print(f"Run ID: {run_id}")
        print(format_trace(result.get("trace", [])))
        print("\n" + result["answer"])
    finally:
        await registry.close()


async def resume_request(run_id: str, approved: bool) -> None:
    store = RunStore()
    state = store.get(run_id)
    if state is None:
        raise SystemExit(f"Run not found: {run_id}")
    registry = await connect_registry()
    try:
        result = await resume_workflow(registry, state, approved)
        store.save(run_id, result)
        print(format_trace(result.get("trace", [])))
        print("\n" + result["answer"])
    finally:
        await registry.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP LangGraph agent")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="start a new agent run")
    run_parser.add_argument("request")
    run_parser.add_argument("--model", action="store_true")
    history_parser = subparsers.add_parser("history", help="list recent runs")
    history_parser.add_argument("--limit", type=int, default=10)
    resume_parser = subparsers.add_parser("resume", help="resume a pending run")
    resume_parser.add_argument("run_id")
    decision = resume_parser.add_mutually_exclusive_group(required=True)
    decision.add_argument("--approve", action="store_true")
    decision.add_argument("--reject", action="store_true")
    subparsers.add_parser("doctor", help="check MCP integration readiness")
    args = parser.parse_args()
    store = RunStore(DB_PATH)
    if args.command == "doctor":
        print(format_checks(readiness_checks()))
    elif args.command == "history":
        print(format_history(store.recent(args.limit)))
    elif args.command == "run":
        asyncio.run(run_request(args.request, "llm" if args.model else "deterministic"))
    else:
        asyncio.run(resume_request(args.run_id, args.approve))


if __name__ == "__main__":
    main()
