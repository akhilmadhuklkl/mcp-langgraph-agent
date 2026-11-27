"""MCP multi-server LangGraph agent."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mcp-langgraph-agent")
except PackageNotFoundError:
    __version__ = "0.1.0"
