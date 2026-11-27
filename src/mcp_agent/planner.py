from typing import Any


def deterministic_plan(request: str) -> list[dict[str, Any]]:
    text = request.lower()
    plan: list[dict[str, Any]] = []
    if "weather" in text or "forecast" in text:
        plan.append({"tool": "weather.forecast", "arguments": {"city": "Bengaluru"}})
    if "calendar" in text or "meeting" in text:
        plan.append({"tool": "calendar.next_meeting", "arguments": {}})
    if "task" in text or "todo" in text:
        plan.append({"tool": "tasks.create_task", "arguments": {"title": "Prepare for the next meeting", "priority": "high"}})
    if not plan:
        plan.append({"tool": "calendar.list_events", "arguments": {"day": "today"}})
    return plan
