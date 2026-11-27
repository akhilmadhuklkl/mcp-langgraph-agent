from mcp_agent.state import initial_state


def test_initial_state_has_explicit_workflow_fields():
    state = initial_state("Search GitHub")
    assert state["request"] == "Search GitHub"
    assert state["planner_mode"] == "deterministic"
    assert state["plan"] == []
    assert state["current_step"] == 0
    assert state["results"] == []
    assert state["trace"] == []
    assert state["errors"] == []
    assert state["approval_status"] == "not_required"
    assert state["answer"] == ""
