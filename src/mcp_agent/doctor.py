import os
import shutil
from dataclasses import dataclass

from .config import github_server_config


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def readiness_checks() -> list[Check]:
    configured = github_server_config()
    docker = shutil.which("docker")
    token = bool(os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"))
    return [
        Check("Docker", "ready" if docker else "missing", "Docker executable detected" if docker else "Install Docker or use a native MCP binary"),
        Check("GitHub command", "ready" if configured else "mock", configured.command if configured else "External command is unset; local mock server will be used"),
        Check("GitHub token", "ready" if token else "missing", "Token is configured" if token else "Set GITHUB_PERSONAL_ACCESS_TOKEN for the external server"),
    ]


def format_checks(checks: list[Check]) -> str:
    lines = ["MCP agent readiness:"]
    for check in checks:
        lines.append(f"  - {check.name}: {check.status} — {check.detail}")
    return "\n".join(lines)
