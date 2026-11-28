"""Compare deterministic plans with expected tool selections."""

import json
from pathlib import Path

from mcp_agent.planner import deterministic_plan

CASES = [
    ("Search Gmail for MCP", "gmail.search_threads"),
    ("Find GitHub issues", "github.search_issues"),
    ("Find Drive documents", "drive.search_files"),
    ("Search Gmail and find Drive documents", "gmail.search_threads"),
]


def evaluate() -> dict[str, object]:
    results = []
    for request, expected_tool in CASES:
        plan = deterministic_plan(request)
        tools = [step["tool"] for step in plan]
        results.append({"request": request, "expected": expected_tool, "tools": tools, "passed": expected_tool in tools})
    passed = sum(item["passed"] for item in results)
    return {"passed": passed, "total": len(results), "accuracy": passed / len(results), "cases": results}


if __name__ == "__main__":
    output_path = Path("data/planner-evaluation.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = evaluate()
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
