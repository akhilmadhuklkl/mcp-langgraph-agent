from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    request: str
    plan: list[dict[str, Any]]
    current_step: int
    results: list[dict[str, Any]]
    trace: list[dict[str, Any]]
    errors: list[dict[str, Any]]
    approval_status: str
    answer: str


def initial_state(request: str) -> AgentState:
    return {
        "request": request,
        "plan": [],
        "current_step": 0,
        "results": [],
        "trace": [],
        "errors": [],
        "approval_status": "not_required",
        "answer": "",
    }
