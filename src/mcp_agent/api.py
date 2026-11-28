"""Minimal authenticated HTTP surface for portfolio deployment demos."""

import asyncio
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .auth import authorize
from .mcp_client import MCPToolRegistry
from .planner import deterministic_plan


class AgentHandler(BaseHTTPRequestHandler):
    server_version = "MCPAgent/1.0"

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        value = self.headers.get("Authorization", "")
        token = value.removeprefix("Bearer ").strip() if value.startswith("Bearer ") else self.headers.get("X-API-Key")
        return authorize(token)

    def do_GET(self) -> None:
        if urlparse(self.path).path == "/health":
            self._send(200, {"status": "ok"})
            return
        if not self._authorized():
            self._send(401, {"error": "authentication required"})
            return
        if urlparse(self.path).path == "/catalog":
            registry = asyncio.run(_registry())
            try:
                self._send(200, {"tools": registry.catalog()})
            finally:
                asyncio.run(registry.close())
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
        if not self._authorized():
            self._send(401, {"error": "authentication required"})
            return
        if urlparse(self.path).path != "/plan":
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            request = str(payload["request"])
            self._send(200, {"steps": deterministic_plan(request)})
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self._send(400, {"error": "body must contain a request string"})

    def log_message(self, format: str, *args: object) -> None:
        return


async def _registry() -> MCPToolRegistry:
    registry = MCPToolRegistry()
    await registry.connect(["github", "gmail", "drive"])
    return registry


def serve(host: str = "127.0.0.1", port: int = 8080) -> None:
    ThreadingHTTPServer((host, port), AgentHandler).serve_forever()


if __name__ == "__main__":
    serve()
