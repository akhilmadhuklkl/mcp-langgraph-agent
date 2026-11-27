import json
import subprocess
import sys


def test_doctor_json_is_structured():
    result = subprocess.run(
        [sys.executable, "-m", "mcp_agent.cli", "doctor", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert any(item["name"] == "Google OAuth client" for item in payload)
    assert all(set(item) == {"name", "status", "detail"} for item in payload)
