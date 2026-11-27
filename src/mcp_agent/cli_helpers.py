from typing import Any


def format_history(items: list[dict[str, Any]]) -> str:
    if not items:
        return "No agent runs found."
    lines = ["Recent agent runs:"]
    for item in items:
        state = item["state"]
        lines.append(
            f"  - {item['run_id']} | status={state.get('approval_status', 'unknown')} "
            f"| request={item['request']} | updated={item['updated_at']}"
        )
    return "\n".join(lines)
