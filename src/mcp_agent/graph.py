from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .mcp_client import MCPToolRegistry
from .planner import deterministic_plan


class AgentState(TypedDict, total=False):
    request: str
    plan: list[dict[str, Any]]
    cursor: int
    results: list[dict[str, Any]]
    answer: str


def build_graph(registry: MCPToolRegistry):
    def plan_node(state: AgentState) -> AgentState:
        return {"plan": deterministic_plan(state["request"]), "cursor": 0, "results": []}

    async def execute_node(state: AgentState) -> AgentState:
        step = state["plan"][state["cursor"]]
        value = await registry.call(step["tool"], step["arguments"])
        results = [*state.get("results", []), {"tool": step["tool"], "result": value}]
        return {"cursor": state["cursor"] + 1, "results": results}

    def should_continue(state: AgentState) -> str:
        return "execute" if state["cursor"] < len(state["plan"]) else "finish"

    def finish_node(state: AgentState) -> AgentState:
        lines = [f"{item['tool']}: {item['result']}" for item in state["results"]]
        return {"answer": "Completed the requested workflow.\n" + "\n".join(lines)}

    workflow = StateGraph(AgentState)
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("finish", finish_node)
    workflow.add_edge(START, "plan")
    workflow.add_conditional_edges("plan", should_continue, {"execute": "execute", "finish": "finish"})
    workflow.add_conditional_edges("execute", should_continue, {"execute": "execute", "finish": "finish"})
    workflow.add_edge("finish", END)
    return workflow.compile()
