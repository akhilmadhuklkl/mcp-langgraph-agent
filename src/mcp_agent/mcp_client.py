from contextlib import AsyncExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@dataclass
class ToolHandle:
    server: str
    name: str
    description: str
    schema: dict[str, Any]


class MCPToolRegistry:
    """Owns MCP sessions and exposes namespaced tools to the graph."""

    def __init__(self) -> None:
        self.stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self.tools: dict[str, ToolHandle] = {}

    async def connect(self, names: list[str]) -> None:
        root = Path(__file__).resolve().parent
        for name in names:
            params = StdioServerParameters(
                command=sys.executable,
                args=[str(root / "server_runner.py"), name],
            )
            read, write = await self.stack.enter_async_context(stdio_client(params))
            session = await self.stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.sessions[name] = session
            result = await session.list_tools()
            for tool in result.tools:
                key = f"{name}.{tool.name}"
                self.tools[key] = ToolHandle(
                    server=name,
                    name=tool.name,
                    description=tool.description or "",
                    schema=tool.inputSchema,
                )

    async def call(self, namespaced_name: str, arguments: dict[str, Any]) -> Any:
        handle = self.tools[namespaced_name]
        result = await self.sessions[handle.server].call_tool(handle.name, arguments)
        values = []
        for content in result.content:
            if hasattr(content, "text"):
                values.append(content.text)
            elif hasattr(content, "data"):
                values.append(content.data)
        return values[0] if len(values) == 1 else values

    async def close(self) -> None:
        await self.stack.aclose()
