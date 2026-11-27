from typing import Any


MUTATING_TOOLS = {
    "github.create_issue",
    "github.create_pull_request",
    "gmail.draft_email",
    "gmail.send_email",
    "notion.create_page",
}


def requires_approval(tool_name: str) -> bool:
    """Return whether a tool can change external data."""
    return tool_name in MUTATING_TOOLS


def approval_message(tool_name: str, arguments: dict[str, Any]) -> str:
    return f"Approval required before running {tool_name} with arguments {arguments}."
