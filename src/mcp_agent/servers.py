from mcp.server.fastmcp import FastMCP


def github_server() -> FastMCP:
    server = FastMCP("github")

    @server.tool()
    def search_issues(query: str = "") -> list[dict[str, str]]:
        """Search open GitHub issues in the local demo workspace."""
        return [
            {"number": "#12", "title": "Add MCP approval checkpoints", "status": "open", "query": query},
            {"number": "#18", "title": "Add tool latency metrics", "status": "open", "query": query},
        ]

    @server.tool()
    def get_pull_request(number: int) -> dict[str, str]:
        """Get a pull request summary."""
        return {"number": str(number), "title": "MCP client improvements", "status": "open", "reviewers": "2"}

    return server


def gmail_server() -> FastMCP:
    server = FastMCP("gmail")

    @server.tool()
    def search_emails(query: str) -> list[dict[str, str]]:
        """Search the local demo inbox."""
        return [{"from": "team@example.com", "subject": "MCP project update", "snippet": "Please review the latest agent workflow.", "query": query}]

    @server.tool()
    def draft_email(to: str, subject: str, body: str) -> dict[str, str]:
        """Create a local demo email draft without sending it."""
        return {"to": to, "subject": subject, "body": body, "status": "draft"}

    return server


def notion_server() -> FastMCP:
    server = FastMCP("notion")

    @server.tool()
    def search_pages(query: str) -> list[dict[str, str]]:
        """Search the local demo Notion workspace."""
        return [{"title": "MCP Agent Project Plan", "url": "notion://mcp-agent-plan", "match": query}]

    @server.tool()
    def create_page(title: str, content: str) -> dict[str, str]:
        """Create a local demo Notion page."""
        return {"title": title, "content": content, "status": "created"}

    return server


def main(server_name: str) -> None:
    servers = {"github": github_server, "gmail": gmail_server, "notion": notion_server}
    servers[server_name]().run(transport="stdio")
