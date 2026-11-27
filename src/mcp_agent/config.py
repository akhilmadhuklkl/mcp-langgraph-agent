import os
import shlex
from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalServerConfig:
    command: str
    args: list[str]
    env: dict[str, str]


def github_server_config() -> ExternalServerConfig | None:
    command = os.getenv("GITHUB_MCP_COMMAND")
    if not command:
        return None
    args = shlex.split(os.getenv("GITHUB_MCP_ARGS", "stdio"))
    env = dict(os.environ)
    return ExternalServerConfig(command=command, args=args, env=env)


def gmail_server_config() -> ExternalServerConfig | None:
    command = os.getenv("GMAIL_MCP_COMMAND")
    if not command:
        return None
    args = shlex.split(os.getenv("GMAIL_MCP_ARGS", "stdio"))
    return ExternalServerConfig(command=command, args=args, env=dict(os.environ))
