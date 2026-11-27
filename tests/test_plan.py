from mcp_agent.planner import deterministic_plan


def test_routes_github_and_gmail_request():
    plan = deterministic_plan("Check GitHub issues and my Gmail inbox")
    assert [step["tool"] for step in plan] == ["github.search_issues", "gmail.search_threads"]


def test_routes_drive():
    plan = deterministic_plan("Find the project documentation in Google Drive")
    assert plan[0]["tool"] == "drive.search_files"
    assert plan[0]["arguments"] == {"query": "name contains 'MCP'"}


def test_uses_real_gmail_search_syntax():
    plan = deterministic_plan("Search my Gmail inbox for MCP")
    assert plan[0]["tool"] == "gmail.search_threads"
    assert plan[0]["arguments"] == {"query": "MCP"}
