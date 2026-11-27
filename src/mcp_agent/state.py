from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    request: str
    planner_mode: str
    plan: list[dict[str, Any]]
    current_step: int
    results: list[dict[str, Any]]
    trace: list[dict[str, Any]]
    errors: list[dict[str, Any]]
    approval_status: str
    answer: str


def initial_state(request: str, planner_mode: str = "deterministic") -> AgentState:
    return {
        "request": request,
        "planner_mode": planner_mode,
        "plan": [],
        "current_step": 0,
        "results": [],
        "trace": [],
        "errors": [],
        "approval_status": "not_required",
        "answer": "",
    }


def apply_approval_decision(state: AgentState, approved: bool) -> AgentState:
    """Return a resumable state after a human approval decision."""
    updated = dict(state)
    updated["approval_status"] = "approved" if approved else "rejected"
    if not approved:
        updated["answer"] = "The pending action was rejected and was not executed."
    return updated
