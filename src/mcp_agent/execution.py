import json
from typing import Any


def resolve_arguments(arguments: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    """Resolve `${last_result}` references against the latest tool result."""
    if not results:
        return arguments
    latest = results[-1].get("result")
    rendered = json.dumps(latest, ensure_ascii=True, sort_keys=True)

    def resolve(value: Any) -> Any:
        if isinstance(value, str):
            return value.replace("${last_result}", rendered)
        if isinstance(value, dict):
            return {key: resolve(item) for key, item in value.items()}
        if isinstance(value, list):
            return [resolve(item) for item in value]
        return value

    return resolve(arguments)
