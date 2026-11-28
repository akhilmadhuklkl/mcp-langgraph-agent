"""Run read-only contract checks against configured external MCP servers."""

import asyncio
from collections.abc import Awaitable, Callable

from mcp_agent.config import (
    drive_server_config,
    github_server_config,
    gmail_server_config,
)
from mcp_agent.mcp_client import MCPToolRegistry


async def verify_server(
    name: str,
    config_factory: Callable[[], object | None],
    tool_name: str,
    arguments: dict[str, object],
) -> None:
    config = config_factory()
    if config is None:
        raise RuntimeError(f"{name} is not configured")
    registry = MCPToolRegistry()
    await registry.connect_external(name, config)
    try:
        discovered = {item["name"] for item in registry.catalog()}
        if tool_name not in discovered:
            raise RuntimeError(f"{tool_name} was not discovered")
        result = await registry.call(tool_name, arguments)
        print(f"PASS {tool_name}: {str(result)[:160]}")
    finally:
        await registry.close()


async def main() -> None:
    checks: list[Awaitable[None]] = [
        verify_server(
            "github",
            github_server_config,
            "github.search_issues",
            {"query": "is:open", "perPage": 1},
        ),
        verify_server(
            "gmail",
            gmail_server_config,
            "gmail.search_threads",
            {"query": "MCP", "pageSize": 1},
        ),
        verify_server(
            "drive",
            drive_server_config,
            "drive.search_files",
            {"query": "name contains 'MCP'", "pageSize": 1},
        ),
    ]
    for check in checks:
        await check


if __name__ == "__main__":
    asyncio.run(main())
