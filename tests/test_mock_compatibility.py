import asyncio

from mcp_agent.mcp_client import MCPToolRegistry


def test_local_servers_expose_live_compatible_tools():
    async def exercise() -> None:
        registry = MCPToolRegistry()
        await registry.connect(["gmail", "drive"])
        try:
            names = {item["name"] for item in registry.catalog()}
            assert "gmail.search_threads" in names
            assert "gmail.create_draft" in names
            assert "drive.search_files" in names

            gmail_result = await registry.call("gmail.search_threads", {"query": "MCP"})
            drive_result = await registry.call("drive.search_files", {"query": "name contains 'MCP'"})
            assert "MCP project update" in gmail_result
            assert "MCP Agent Project Plan" in drive_result
        finally:
            await registry.close()

    asyncio.run(exercise())
