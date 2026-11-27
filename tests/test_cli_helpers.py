from mcp_agent.cli_helpers import format_history


def test_formats_run_history():
    output = format_history([{"run_id": "abc", "request": "Search GitHub", "updated_at": "now", "state": {"approval_status": "not_required"}}])
    assert "abc" in output
    assert "Search GitHub" in output
    assert "not_required" in output


def test_formats_empty_history():
    assert format_history([]) == "No agent runs found."
