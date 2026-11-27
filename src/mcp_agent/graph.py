from typing import Any
from time import perf_counter

from langgraph.graph import END, START, StateGraph

from .mcp_client import MCPToolRegistry
from .execution import resolve_arguments
from .planner import deterministic_plan, llm_plan
from .state import AgentState


def build_graph(registry: MCPToolRegistry):
    async def plan_node(state: AgentState) -> AgentState:
        if state.get("planner_mode") == "llm":
            plan = await llm_plan(state["request"], registry.catalog())
        else:
            plan = deterministic_plan(state["request"])
        return {
            "plan": plan,
            "current_step": 0,
            "results": [],
            "trace": [],
            "errors": [],
            "approval_status": "not_required",
        }

    async def execute_node(state: AgentState) -> AgentState:
        step = state["plan"][state["current_step"]]
        started = perf_counter()
        resolved_arguments = resolve_arguments(step["arguments"], state.get("results", []))
        trace_item: dict[str, Any] = {
            "tool": step["tool"],
            "arguments": resolved_arguments,
            "status": "success",
        }
        try:
            value = await registry.call(step["tool"], resolved_arguments)
            results = [*state.get("results", []), {"tool": step["tool"], "result": value}]
        except Exception as exc:  # noqa: BLE001 - trace and surface tool failures
            value = {"error": str(exc)}
            trace_item["status"] = "error"
            trace_item["error"] = str(exc)
            results = [*state.get("results", []), {"tool": step["tool"], "result": value}]
        trace_item["duration_ms"] = (perf_counter() - started) * 1000
        return {
            "current_step": state["current_step"] + 1,
            "results": results,
            "trace": [*state.get("trace", []), trace_item],
            "errors": [
                *state.get("errors", []),
                *([{"tool": step["tool"], "message": str(exc)}] if trace_item["status"] == "error" else []),
            ],
        }

    def should_continue(state: AgentState) -> str:
        return "execute" if state["current_step"] < len(state["plan"]) else "finish"

    def finish_node(state: AgentState) -> AgentState:
        lines = [f"{item['tool']}: {item['result']}" for item in state["results"]]
        prefix = "Completed the requested workflow."
        if state.get("errors"):
            prefix = "Completed the workflow with errors."
        return {"answer": prefix + "\n" + "\n".join(lines)}

    workflow = StateGraph(AgentState)
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("finish", finish_node)
    workflow.add_edge(START, "plan")
    workflow.add_conditional_edges("plan", should_continue, {"execute": "execute", "finish": "finish"})
    workflow.add_conditional_edges("execute", should_continue, {"execute": "execute", "finish": "finish"})
    workflow.add_edge("finish", END)
    return workflow.compile()
