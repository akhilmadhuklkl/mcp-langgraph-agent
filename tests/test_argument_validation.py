import pytest

from mcp_agent.mcp_client import MCPToolRegistry, ToolHandle


def test_argument_validation_rejects_unknown_argument():
    handle = ToolHandle("gmail", "search_threads", "", {"properties": {"query": {}}})
    with pytest.raises(ValueError, match="unknown arguments: typo"):
        MCPToolRegistry._validate_arguments(handle, {"typo": "MCP"})


def test_argument_validation_rejects_missing_required_argument():
    handle = ToolHandle("drive", "get_file_metadata", "", {"properties": {"fileId": {}}, "required": ["fileId"]})
    with pytest.raises(ValueError, match="missing required arguments: fileId"):
        MCPToolRegistry._validate_arguments(handle, {})
