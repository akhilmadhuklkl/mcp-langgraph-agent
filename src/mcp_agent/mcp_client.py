from contextlib import AsyncExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import sys
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .reliability import retry_count, retry_delay
from .config import ExternalServerConfig


@dataclass
class ToolHandle:
    server: str
    name: str
    description: str
    schema: dict[str, Any]

    @property
    def qualified_name(self) -> str:
        return f"{self.server}.{self.name}"

    @property
    def input_names(self) -> list[str]:
        return sorted(self.schema.get("properties", {}).keys())


class MCPToolRegistry:
    """Owns MCP sessions and exposes namespaced tools to the graph."""

    def __init__(self, timeout_seconds: float = 30.0, max_retries: int = 2) -> None:
        self.stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self.tools: dict[str, ToolHandle] = {}
        self.timeout_seconds = timeout_seconds
        self.max_retries = retry_count(max_retries)

    async def connect(self, names: list[str]) -> None:
        root = Path(__file__).resolve().parent
        for name in names:
            params = StdioServerParameters(
                command=sys.executable,
                args=[str(root / "server_runner.py"), name],
            )
            await self._connect_with_params(name, params)

    async def connect_external(self, name: str, config: ExternalServerConfig) -> None:
        params = StdioServerParameters(command=config.command, args=config.args, env=config.env)
        await self._connect_with_params(name, params)

    async def _connect_with_params(self, name: str, params: StdioServerParameters) -> None:
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

    def catalog(self) -> list[dict[str, Any]]:
        """Return stable, presentation-friendly metadata for discovered tools."""
        return [
            {
                "name": handle.qualified_name,
                "server": handle.server,
                "description": handle.description,
                "inputs": handle.input_names,
            }
            for handle in sorted(self.tools.values(), key=lambda item: item.qualified_name)
        ]

    async def call(self, namespaced_name: str, arguments: dict[str, Any]) -> Any:
        handle = self.tools[namespaced_name]
        self._validate_arguments(handle, arguments)
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 2):
            try:
                result = await asyncio.wait_for(
                    self.sessions[handle.server].call_tool(handle.name, arguments),
                    timeout=self.timeout_seconds,
                )
                break
            except Exception as exc:  # noqa: BLE001 - retry then surface the final error
                last_error = exc
                if attempt > self.max_retries:
                    raise RuntimeError(
                        f"MCP tool {namespaced_name} failed after {attempt} attempt(s): {exc}"
                    ) from exc
                await asyncio.sleep(retry_delay(attempt))
        else:  # pragma: no cover - loop always returns or raises
            raise RuntimeError(f"MCP tool {namespaced_name} failed: {last_error}")
        values = []
        for content in result.content:
            if hasattr(content, "text"):
                values.append(content.text)
            elif hasattr(content, "data"):
                values.append(content.data)
        return values[0] if len(values) == 1 else values

    @staticmethod
    def _validate_arguments(handle: ToolHandle, arguments: dict[str, Any]) -> None:
        properties = set(handle.schema.get("properties", {}))
        required = set(handle.schema.get("required", []))
        missing = sorted(required - arguments.keys())
        unknown = sorted(set(arguments) - properties) if properties else []
        if missing or unknown:
            details = []
            if missing:
                details.append(f"missing required arguments: {', '.join(missing)}")
            if unknown:
                details.append(f"unknown arguments: {', '.join(unknown)}")
            raise ValueError(f"Invalid arguments for {handle.qualified_name}: {'; '.join(details)}")

    async def close(self) -> None:
        await self.stack.aclose()
