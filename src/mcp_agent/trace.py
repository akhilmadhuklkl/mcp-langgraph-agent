from typing import Any

SENSITIVE_KEYS = {"body", "content", "password", "secret", "token", "access_token", "refresh_token"}


def redact_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return trace-safe arguments without common credential or message fields."""
    return {
        key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else value
        for key, value in arguments.items()
    }


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
