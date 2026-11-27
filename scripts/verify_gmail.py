import asyncio

from mcp_agent.config import gmail_server_config
from mcp_agent.mcp_client import MCPToolRegistry


async def main() -> None:
    config = gmail_server_config()
    if config is None:
        raise SystemExit("Gmail MCP is not configured")
    registry = MCPToolRegistry()
    await registry.connect_external("gmail", config)
    try:
        print("Discovered tools:")
        for tool in registry.catalog():
            print(f"- {tool['name']} inputs={tool['inputs']}")
        result = await registry.call(
            "gmail.search_threads",
            {"query": "MCP", "pageSize": 1},
        )
        print("Read-only search succeeded:", result)
    finally:
        await registry.close()


if __name__ == "__main__":
    asyncio.run(main())
