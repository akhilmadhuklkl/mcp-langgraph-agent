import json
import os
import subprocess
import sys


def test_cli_uses_configured_database_path(tmp_path):
    database_path = tmp_path / "isolated-runs.db"
    environment = os.environ.copy()
    environment["MCP_AGENT_DB_PATH"] = str(database_path)
    result = subprocess.run(
        [sys.executable, "-m", "mcp_agent.cli", "history", "--json"],
        capture_output=True,
        text=True,
        check=True,
        env=environment,
    )

    assert json.loads(result.stdout) == []
    assert database_path.exists()
