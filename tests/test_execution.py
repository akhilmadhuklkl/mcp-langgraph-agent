from mcp_agent.execution import resolve_arguments


def test_resolves_latest_result_in_nested_arguments():
    result = resolve_arguments(
        {"query": "Related to ${last_result}", "options": {"limit": 3}},
        [{"tool": "github.search_issues", "result": [{"number": "#12"}]}],
    )
    assert result["query"] == 'Related to [{"number": "#12"}]'
    assert result["options"]["limit"] == 3


def test_keeps_arguments_when_no_previous_result_exists():
    arguments = {"query": "MCP"}
    assert resolve_arguments(arguments, []) == arguments
