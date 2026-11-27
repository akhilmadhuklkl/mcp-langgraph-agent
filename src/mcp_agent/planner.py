from typing import Any


def deterministic_plan(request: str) -> list[dict[str, Any]]:
    text = request.lower()
    plan: list[dict[str, Any]] = []
    if "github" in text or "issue" in text or "pull request" in text:
        plan.append({"tool": "github.search_issues", "arguments": {"query": "open"}})
    if "email" in text or "gmail" in text or "inbox" in text:
        plan.append({"tool": "gmail.search_emails", "arguments": {"query": "MCP"}})
    if "notion" in text or "notes" in text or "documentation" in text:
        plan.append({"tool": "notion.search_pages", "arguments": {"query": "MCP"}})
    if not plan:
        plan.append({"tool": "github.search_issues", "arguments": {"query": "open"}})
    return plan
