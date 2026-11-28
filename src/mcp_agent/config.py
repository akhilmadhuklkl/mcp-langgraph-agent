import os
import shlex
from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalServerConfig:
    command: str
    args: list[str]
    env: dict[str, str]


@dataclass(frozen=True)
class StreamableHTTPServerConfig:
    name: str
    url: str


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


def drive_server_config() -> ExternalServerConfig | None:
    command = os.getenv("GOOGLE_DRIVE_MCP_COMMAND")
    if not command:
        return None
    args = shlex.split(os.getenv("GOOGLE_DRIVE_MCP_ARGS", "stdio"))
    return ExternalServerConfig(command=command, args=args, env=dict(os.environ))


def spotify_server_config() -> ExternalServerConfig | None:
    command = os.getenv("SPOTIFY_MCP_COMMAND")
    if not command:
        return None
    args = shlex.split(os.getenv("SPOTIFY_MCP_ARGS", "stdio"))
    return ExternalServerConfig(command=command, args=args, env=dict(os.environ))


def streamable_http_server_config() -> StreamableHTTPServerConfig | None:
    url = os.getenv("MCP_HTTP_SERVER_URL")
    if not url:
        return None
    return StreamableHTTPServerConfig(os.getenv("MCP_HTTP_SERVER_NAME", "remote"), url)
