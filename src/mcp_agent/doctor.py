import os
import shutil
from dataclasses import dataclass

from .config import drive_server_config, gmail_server_config, github_server_config


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def readiness_checks() -> list[Check]:
    configured = github_server_config()
    docker = shutil.which("docker")
    token = bool(os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"))
    gmail_config = gmail_server_config()
    drive_config = drive_server_config()
    oauth_json = os.getenv("GOOGLE_OAUTH_CLIENT_JSON")
    oauth_ready = bool(oauth_json and os.path.isfile(oauth_json))
    return [
        Check("Docker", "ready" if docker else "missing", "Docker executable detected" if docker else "Install Docker or use a native MCP binary"),
        Check("GitHub command", "ready" if configured else "mock", configured.command if configured else "External command is unset; local mock server will be used"),
        Check("GitHub token", "ready" if token else "missing", "Token is configured" if token else "Set GITHUB_PERSONAL_ACCESS_TOKEN for the external server"),
        Check("Gmail command", "ready" if gmail_config else "mock", gmail_config.command if gmail_config else "External command is unset; local mock server will be used"),
        Check("Google Drive command", "ready" if drive_config else "mock", drive_config.command if drive_config else "External command is unset; local mock server will be used"),
        Check("Google OAuth client", "ready" if oauth_ready else "missing", "OAuth client JSON found" if oauth_ready else "Set GOOGLE_OAUTH_CLIENT_JSON to the downloaded client JSON path"),
    ]


def format_checks(checks: list[Check]) -> str:
    lines = ["MCP agent readiness:"]
    for check in checks:
        lines.append(f"  - {check.name}: {check.status} — {check.detail}")
    return "\n".join(lines)
