from typing import Any


def format_catalog(entries: list[dict[str, Any]]) -> str:
    """Format discovered MCP tools for a human-readable CLI trace."""
    if not entries:
        return "No MCP tools discovered."
    lines = ["Discovered MCP tools:"]
    for entry in entries:
        inputs = ", ".join(entry["inputs"]) or "no inputs"
        lines.append(f"  - {entry['name']}: {entry['description']} (inputs: {inputs})")
    return "\n".join(lines)
