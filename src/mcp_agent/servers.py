from mcp.server.fastmcp import FastMCP


def calendar_server() -> FastMCP:
    server = FastMCP("calendar")

    @server.tool()
    def list_events(day: str = "today") -> list[dict[str, str]]:
        """List calendar events for a relative day."""
        return [
            {"title": "Design review", "start": "10:00", "end": "11:00", "day": day},
            {"title": "Team standup", "start": "15:00", "end": "15:30", "day": day},
        ]

    @server.tool()
    def next_meeting() -> dict[str, str]:
        """Return the next meeting."""
        return {"title": "Design review", "start": "10:00", "day": "today"}

    return server


def tasks_server() -> FastMCP:
    server = FastMCP("tasks")
    tasks: list[dict[str, str]] = []

    @server.tool()
    def create_task(title: str, priority: str = "normal") -> dict[str, str]:
        """Create a task in the local demo task list."""
        item = {"title": title, "priority": priority, "status": "open"}
        tasks.append(item)
        return item

    @server.tool()
    def list_tasks() -> list[dict[str, str]]:
        """List open tasks."""
        return tasks

    return server


def weather_server() -> FastMCP:
    server = FastMCP("weather")

    @server.tool()
    def forecast(city: str) -> dict[str, str]:
        """Return a deterministic demo forecast."""
        return {"city": city, "condition": "partly cloudy", "temperature": "27 C"}

    return server


def main(server_name: str) -> None:
    servers = {"calendar": calendar_server, "tasks": tasks_server, "weather": weather_server}
    servers[server_name]().run(transport="stdio")
