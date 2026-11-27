from typing import Any

SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "body",
    "client_secret",
    "content",
    "password",
    "secret",
    "token",
    "access_token",
    "refresh_token",
}


def _redact_value(key: str, value: Any) -> Any:
    normalized_key = key.lower().replace("-", "_")
    if normalized_key in SENSITIVE_KEYS or normalized_key.endswith(("_key", "_secret", "_token")):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {nested_key: _redact_value(nested_key, nested_value) for nested_key, nested_value in value.items()}
    if isinstance(value, list):
        return [_redact_value("", item) for item in value]
    return value


def redact_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return trace-safe arguments without common credential or message fields."""
    return {key: _redact_value(key, value) for key, value in arguments.items()}


def format_trace(trace: list[dict[str, Any]]) -> str:
    """Format tool execution records for the CLI."""
    if not trace:
        return "Execution trace: no tool calls."
    lines = ["Execution trace:"]
    for index, item in enumerate(trace, start=1):
        lines.append(
            f"  {index}. {item['tool']} | status={item['status']} "
            f"| duration={item['duration_ms']:.2f}ms "
            f"| arguments={redact_arguments(item['arguments'])}"
        )
        if item.get("error"):
            lines.append(f"     error: {redact_arguments({'error': item['error']})['error']}")
    return "\n".join(lines)
