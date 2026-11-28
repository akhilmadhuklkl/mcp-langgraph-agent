import argparse
import asyncio
import csv
import json
import os
import sys
from html import escape

from . import __version__
from .cli_helpers import format_history
from .config import (
    drive_server_config,
    github_server_config,
    gmail_server_config,
    spotify_server_config,
    streamable_http_server_config,
)
from .doctor import format_checks, readiness_checks
from .graph import build_graph, resume_workflow
from .mcp_client import MCPToolRegistry
from .persistence import RunStore
from .planner import deterministic_plan
from .state import initial_state
from .trace import format_trace

DB_PATH = os.getenv("MCP_AGENT_DB_PATH", "data/agent_runs.db")


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
    drive_config = drive_server_config()
    if drive_config:
        await registry.connect_external("drive", drive_config)
    else:
        await registry.connect(["drive"])
    spotify_config = spotify_server_config()
    if spotify_config:
        await registry.connect_external("spotify", spotify_config)
    else:
        await registry.connect(["spotify"])
    http_config = streamable_http_server_config()
    if http_config:
        await registry.connect_streamable_http(http_config.name, http_config.url)
    return registry


async def run_request(request: str, planner_mode: str, json_output: bool = False) -> None:
    store = RunStore()
    state = initial_state(request, planner_mode)
    run_id = store.create(request, state)
    state["run_id"] = run_id
    store.save(run_id, state)
    registry = await connect_registry()
    try:
        result = await build_graph(registry).ainvoke(state)
        store.save(run_id, result)
        if json_output:
            print(
                json.dumps(
                    {
                        "run_id": run_id,
                        "answer": result["answer"],
                        "trace": result.get("trace", []),
                        "metrics": registry.metrics(),
                    },
                    indent=2,
                )
            )
            return
        print(f"Run ID: {run_id}")
        print(format_trace(result.get("trace", [])))
        print_metrics(registry.metrics())
        print("\n" + result["answer"])
    finally:
        await registry.close()


async def catalog_request(json_output: bool = False) -> None:
    registry = await connect_registry()
    try:
        if json_output:
            print(json.dumps(registry.catalog(), indent=2))
            return
        print("Discovered MCP tools:")
        for item in registry.catalog():
            print(f"  - {item['name']} | inputs={', '.join(item['inputs']) or 'none'}")
    finally:
        await registry.close()


def print_metrics(metrics: list[dict[str, object]]) -> None:
    if not metrics:
        return
    print("\nTool metrics:")
    for item in metrics:
        print(
            f"  {item['tool']} | calls={item['calls']} | successes={item['successes']} "
            f"| failures={item['failures']} | retries={item['retries']} "
            f"| average={item['average_duration_ms']:.2f}ms"
        )


def aggregate_run_metrics(runs: list[dict[str, object]]) -> list[dict[str, object]]:
    aggregate: dict[str, dict[str, float]] = {}
    for run in runs:
        state = run.get("state", {})
        for item in state.get("trace", []):
            tool = item["tool"]
            values = aggregate.setdefault(tool, {"calls": 0, "successes": 0, "failures": 0, "duration_ms": 0})
            values["calls"] += 1
            values["successes"] += item.get("status") == "success"
            values["failures"] += item.get("status") == "error"
            values["duration_ms"] += item.get("duration_ms", 0)
    return [
        {
            "tool": tool,
            "calls": int(values["calls"]),
            "successes": int(values["successes"]),
            "failures": int(values["failures"]),
            "average_duration_ms": values["duration_ms"] / values["calls"],
        }
        for tool, values in sorted(aggregate.items())
    ]


def render_metrics_html(metrics: list[dict[str, object]]) -> str:
    rows = "\n".join(
        "<tr>"
        + "".join(f"<td>{escape(str(item[field]))}</td>" for field in metrics[0])
        + "</tr>"
        for item in metrics
    )
    headers = "".join(f"<th>{escape(str(field))}</th>" for field in (metrics[0] if metrics else []))
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>MCP Agent Metrics</title><style>body{font-family:system-ui;margin:2rem}"
        "table{border-collapse:collapse}th,td{border:1px solid #ccc;padding:.5rem}"
        "th{background:#eee}</style></head><body><h1>MCP Agent Metrics</h1>"
        f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"
        "</body></html>"
    )


def print_plan(request: str, json_output: bool = False) -> None:
    plan = deterministic_plan(request)
    if json_output:
        print(json.dumps(plan, indent=2))
        return
    print("Planned MCP steps:")
    for index, step in enumerate(plan, start=1):
        print(f"  {index}. {step['tool']} | arguments={step['arguments']}")


async def resume_request(run_id: str, approved: bool, json_output: bool = False) -> None:
    store = RunStore()
    state = store.get(run_id)
    if state is None:
        raise SystemExit(f"Run not found: {run_id}")
    registry = await connect_registry()
    try:
        result = await resume_workflow(registry, state, approved)
        store.save(run_id, result)
        if json_output:
            print(
                json.dumps(
                    {
                        "run_id": run_id,
                        "answer": result["answer"],
                        "trace": result.get("trace", []),
                        "metrics": registry.metrics(),
                    },
                    indent=2,
                )
            )
            return
        print(format_trace(result.get("trace", [])))
        print_metrics(registry.metrics())
        print("\n" + result["answer"])
    finally:
        await registry.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP LangGraph agent")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="start a new agent run")
    run_parser.add_argument("request")
    run_parser.add_argument("--model", action="store_true")
    run_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    history_parser = subparsers.add_parser("history", help="list recent runs")
    history_parser.add_argument("--limit", type=int, default=10)
    history_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    metrics_parser = subparsers.add_parser("metrics", help="summarize persisted tool metrics")
    metrics_parser.add_argument("--limit", type=int, default=100)
    metrics_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    metrics_parser.add_argument("--csv", action="store_true", help="emit CSV for spreadsheet tools")
    metrics_parser.add_argument("--html", action="store_true", help="emit a standalone HTML report")
    resume_parser = subparsers.add_parser("resume", help="resume a pending run")
    resume_parser.add_argument("run_id")
    decision = resume_parser.add_mutually_exclusive_group(required=True)
    decision.add_argument("--approve", action="store_true")
    decision.add_argument("--reject", action="store_true")
    resume_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    doctor_parser = subparsers.add_parser("doctor", help="check MCP integration readiness")
    doctor_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    catalog_parser = subparsers.add_parser("catalog", help="discover configured MCP tools")
    catalog_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    plan_parser = subparsers.add_parser("plan", help="show a plan without executing it")
    plan_parser.add_argument("request")
    plan_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    store = RunStore(DB_PATH)
    if args.command == "doctor":
        checks = readiness_checks()
        print(
            json.dumps([check.__dict__ for check in checks], indent=2)
            if args.json
            else format_checks(checks)
        )
    elif args.command == "catalog":
        asyncio.run(catalog_request(args.json))
    elif args.command == "plan":
        print_plan(args.request, args.json)
    elif args.command == "history":
        runs = store.recent(args.limit)
        print(json.dumps(runs, indent=2, default=str) if args.json else format_history(runs))
    elif args.command == "metrics":
        metrics = aggregate_run_metrics(store.recent(args.limit))
        if args.html:
            print(render_metrics_html(metrics))
        elif args.csv:
            writer = csv.DictWriter(sys.stdout, fieldnames=["tool", "calls", "successes", "failures", "average_duration_ms"])
            writer.writeheader()
            writer.writerows(metrics)
        elif args.json:
            print(json.dumps(metrics, indent=2))
        else:
            print_metrics(metrics)
    elif args.command == "run":
        asyncio.run(run_request(args.request, "llm" if args.model else "deterministic", args.json))
    else:
        asyncio.run(resume_request(args.run_id, args.approve, args.json))


if __name__ == "__main__":
    main()
