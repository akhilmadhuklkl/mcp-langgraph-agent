"""Small Spotify Web API MCP bridge.

The access token is supplied through SPOTIFY_ACCESS_TOKEN so secrets never
enter the repository. Obtain it through Spotify OAuth (Authorization Code or
PKCE) before launching this process.
"""

import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from mcp.server.fastmcp import FastMCP

API = "https://api.spotify.com/v1"
server = FastMCP("spotify")


def spotify_get(path: str, params: dict[str, str] | None = None) -> dict:
    token = os.getenv("SPOTIFY_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("SPOTIFY_ACCESS_TOKEN is not configured")
    url = f"{API}{path}"
    if params:
        url += "?" + urlencode(params)
    request = Request(url, headers={"Authorization": f"Bearer {token}"})
    with urlopen(request, timeout=20) as response:
        return json.load(response)


@server.tool()
def search(query: str, kind: str = "track", limit: int = 10) -> list[dict]:
    """Search Spotify's catalog for tracks, artists, albums, or playlists."""
    data = spotify_get("/search", {"q": query, "type": kind, "limit": str(min(max(limit, 1), 50))})
    items = data.get(f"{kind}s", {}).get("items", [])
    return [{"name": item.get("name"), "uri": item.get("uri"), "url": item.get("external_urls", {}).get("spotify")} for item in items]


@server.tool()
def current_user() -> dict:
    """Return the authenticated Spotify user's profile."""
    return spotify_get("/me")


@server.tool()
def my_playlists(limit: int = 20) -> list[dict]:
    """List playlists visible to the authenticated user."""
    data = spotify_get("/me/playlists", {"limit": str(min(max(limit, 1), 50))})
    return [{"name": item.get("name"), "id": item.get("id"), "uri": item.get("uri"), "url": item.get("external_urls", {}).get("spotify")} for item in data.get("items", [])]


if __name__ == "__main__":
    server.run(transport="stdio")
