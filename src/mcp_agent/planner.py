import os
from typing import Any


def ollama_settings() -> tuple[str, str] | None:
    """Return local Ollama model and endpoint when configured."""
    model = os.getenv("OLLAMA_MODEL")
    if not model:
        return None
    return model, os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")


def deterministic_plan(request: str) -> list[dict[str, Any]]:
    text = request.lower()
    plan: list[dict[str, Any]] = []
    if "github" in text or "issue" in text or "pull request" in text:
        plan.append({"tool": "github.search_issues", "arguments": {"query": "open"}})
    if "drive" in text or "google drive" in text or "document" in text or "documentation" in text:
        # Drive search_files expects a Google Drive query expression, not a
        # free-form keyword. Keep the deterministic default read-only.
        query = "name contains 'MCP'"
        plan.append({"tool": "drive.search_files", "arguments": {"query": query}})
    if "email" in text or "gmail" in text or "inbox" in text:
        # The official Gmail MCP server exposes search_threads; the local mock
        # keeps search_emails for backward-compatible offline tests.
        # Gmail uses Gmail search syntax; do not pass serialized output from a
        # previous server as a query.
        plan.append({"tool": "gmail.search_threads", "arguments": {"query": "MCP"}})
    if "spotify" in text or "playlist" in text or "music" in text or "song" in text:
        plan.append({"tool": "spotify.search", "arguments": {"query": "favorite"}})
    if not plan:
        plan.append({"tool": "github.search_issues", "arguments": {"query": "open"}})
    return plan


async def llm_plan(request: str, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate a validated tool plan using an optional LangChain model."""
    try:
        from langchain_openai import ChatOpenAI
        from pydantic import BaseModel, Field
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
    ollama = ollama_settings()
    if ollama:
        ollama_model, ollama_base_url = ollama
        model = ChatOpenAI(
            model=ollama_model,
            temperature=0,
            base_url=ollama_base_url,
            api_key="ollama",
        )
    else:
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    result = await model.with_structured_output(Plan).ainvoke(prompt)
    return [step.model_dump() for step in result.steps]
