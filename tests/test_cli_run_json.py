import json
import subprocess
import sys


def test_run_json_contains_execution_fields():
    result = subprocess.run(
        [sys.executable, "-m", "mcp_agent.cli", "run", "Search Gmail for MCP", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["run_id"]
    assert "gmail.search_threads" in payload["answer"]
    assert payload["trace"][0]["tool"] == "gmail.search_threads"
    assert payload["metrics"][0]["calls"] == 1
