from typing import Any


def format_trace(trace: list[dict[str, Any]]) -> str:
    """Format tool execution records for the CLI."""
    if not trace:
        return "Execution trace: no tool calls."
    lines = ["Execution trace:"]
    for index, item in enumerate(trace, start=1):
        lines.append(
            f"  {index}. {item['tool']} | status={item['status']} "
            f"| duration={item['duration_ms']:.2f}ms | arguments={item['arguments']}"
        )
        if item.get("error"):
            lines.append(f"     error: {item['error']}")
    return "\n".join(lines)
