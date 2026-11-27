import json
import subprocess
import sys


def run_cli(*arguments: str) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "mcp_agent.cli", *arguments],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def test_plan_json_is_structured():
    payload = json.loads(run_cli("plan", "Search Gmail for MCP", "--json"))
    assert payload == [{"tool": "gmail.search_threads", "arguments": {"query": "MCP"}}]


def test_catalog_json_contains_namespaced_mock_tools():
    payload = json.loads(run_cli("catalog", "--json"))
    names = {item["name"] for item in payload}
    assert "github.search_issues" in names
    assert "gmail.search_threads" in names
    assert "drive.search_files" in names
