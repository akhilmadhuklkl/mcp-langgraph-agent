from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest

from mcp_agent import mcp_client
from mcp_agent.mcp_client import MCPToolRegistry


class FakeSession:
    def __init__(self, read, write):
        self.read = read
        self.write = write

    async def initialize(self):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def list_tools(self):
        return SimpleNamespace(
            tools=[
                SimpleNamespace(
                    name="search",
                    description="Search remote records",
                    inputSchema={"properties": {"query": {"type": "string"}}},
                )
            ]
        )


@pytest.mark.asyncio
async def test_connect_streamable_http_discovers_namespaced_tools(monkeypatch):
    @asynccontextmanager
    async def fake_http_client(url):
        assert url == "https://example.test/mcp"
        yield "read", "write", lambda: "session-id"

    monkeypatch.setattr(mcp_client, "streamable_http_client", fake_http_client)
    monkeypatch.setattr(mcp_client, "ClientSession", FakeSession)
    registry = MCPToolRegistry()

    await registry.connect_streamable_http("remote", "https://example.test/mcp")

    assert registry.catalog() == [
        {
            "name": "remote.search",
            "server": "remote",
            "description": "Search remote records",
            "inputs": ["query"],
        }
    ]
    await registry.close()
