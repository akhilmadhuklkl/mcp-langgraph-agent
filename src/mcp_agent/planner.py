from typing import Any


def deterministic_plan(request: str) -> list[dict[str, Any]]:
    text = request.lower()
    plan: list[dict[str, Any]] = []
    if "github" in text or "issue" in text or "pull request" in text:
        plan.append({"tool": "github.search_issues", "arguments": {"query": "open"}})
    if "drive" in text or "google drive" in text or "document" in text or "documentation" in text:
        query = "${last_result}" if plan else "MCP"
        plan.append({"tool": "drive.search_files", "arguments": {"query": query}})
    if "email" in text or "gmail" in text or "inbox" in text:
        query = "${last_result}" if plan else "MCP"
        # The official Gmail MCP server exposes search_threads; the local mock
        # keeps search_emails for backward-compatible offline tests.
        plan.append({"tool": "gmail.search_threads", "arguments": {"query": query}})
    if not plan:
        plan.append({"tool": "github.search_issues", "arguments": {"query": "open"}})
    return plan


async def llm_plan(request: str, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate a validated tool plan using an optional LangChain model."""
    try:
        from pydantic import BaseModel, Field
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError("Install the model extra with: pip install -e '.[model]'") from exc

    class PlannedStep(BaseModel):
        tool: str = Field(description="Exact namespaced MCP tool name")
        arguments: dict[str, Any] = Field(default_factory=dict)

    class Plan(BaseModel):
        steps: list[PlannedStep] = Field(default_factory=list)

    tool_text = "\n".join(
        f"- {item['name']}: {item['description']}; inputs={item['inputs']}"
        for item in tools
    )
    prompt = (
        "You are an MCP tool planner. Create the smallest valid multi-step plan "
        "that satisfies the user's request. Use only the exact tool names provided. "
        "Do not invent tools or arguments. Prefer read-only tools and never send "
        "messages or mutate data unless the user explicitly requests it.\n\n"
        f"Available tools:\n{tool_text}\n\nUser request: {request}"
    )
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    result = await model.with_structured_output(Plan).ainvoke(prompt)
    return [step.model_dump() for step in result.steps]
