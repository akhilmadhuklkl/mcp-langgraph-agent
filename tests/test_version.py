import subprocess
import sys

from mcp_agent import __version__


def test_version_is_defined():
    assert __version__ == "0.1.0"


def test_cli_prints_version():
    result = subprocess.run(
        [sys.executable, "-m", "mcp_agent.cli", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == __version__
