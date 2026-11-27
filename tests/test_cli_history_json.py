import json
import subprocess
import sys


def test_history_json_is_structured():
    result = subprocess.run(
        [sys.executable, "-m", "mcp_agent.cli", "history", "--json", "--limit", "1"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert isinstance(payload, list)
