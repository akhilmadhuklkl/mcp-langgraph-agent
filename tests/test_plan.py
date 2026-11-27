from mcp_agent.planner import deterministic_plan


def test_routes_calendar_and_task_request():
    plan = deterministic_plan("Check my calendar and create a task")
    assert [step["tool"] for step in plan] == ["calendar.next_meeting", "tasks.create_task"]


def test_routes_weather():
    plan = deterministic_plan("What is the weather forecast?")
    assert plan[0]["tool"] == "weather.forecast"
