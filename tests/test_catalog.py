from mcp_agent.catalog import format_catalog


def test_formats_tool_metadata():
    output = format_catalog([
        {
            "name": "github.search_issues",
            "description": "Search open issues",
            "inputs": ["query"],
        }
    ])
    assert "github.search_issues" in output
    assert "Search open issues" in output
    assert "inputs: query" in output


def test_formats_empty_catalog():
    assert format_catalog([]) == "No MCP tools discovered."
