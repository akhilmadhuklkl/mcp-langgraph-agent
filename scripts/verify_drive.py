import asyncio

from mcp_agent.config import drive_server_config
from mcp_agent.mcp_client import MCPToolRegistry


async def main() -> None:
    config = drive_server_config()
    if config is None:
        raise SystemExit("Google Drive MCP is not configured")
    registry = MCPToolRegistry()
    await registry.connect_external("drive", config)
    try:
        for tool in registry.catalog():
            print(f"{tool['name']} inputs={tool['inputs']}")
        result = await registry.call(
            "drive.search_files",
            {"query": "name contains 'MCP'", "pageSize": 1},
        )
        print("Read-only search succeeded:", result)
    finally:
        await registry.close()


if __name__ == "__main__":
    asyncio.run(main())
