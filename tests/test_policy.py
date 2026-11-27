from mcp_agent.policy import approval_message, requires_approval


def test_mutating_tools_require_approval():
    assert requires_approval("notion.create_page")
    assert requires_approval("gmail.draft_email")
    assert not requires_approval("github.search_issues")


def test_approval_message_contains_action_and_arguments():
    message = approval_message("notion.create_page", {"title": "Plan"})
    assert "Approval required" in message
    assert "notion.create_page" in message
    assert "Plan" in message
