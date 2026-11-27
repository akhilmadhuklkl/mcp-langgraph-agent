from mcp_agent.state import apply_approval_decision, initial_state


def test_approval_continues_from_existing_plan():
    state = initial_state("Create a Notion page")
    state["plan"] = [{"tool": "notion.create_page", "arguments": {"title": "Plan"}}]
    state["approval_status"] = "pending"
    state["current_step"] = 0
    resumed = apply_approval_decision(state, approved=True)
    assert resumed["approval_status"] == "approved"
    assert resumed["plan"] == state["plan"]
    assert resumed["current_step"] == 0


def test_rejection_has_safe_answer():
    resumed = apply_approval_decision(initial_state("Create a page"), approved=False)
    assert resumed["approval_status"] == "rejected"
    assert "rejected" in resumed["answer"]
