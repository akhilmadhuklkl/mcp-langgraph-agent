from mcp_agent.config import spotify_server_config


def test_spotify_config_is_mock_by_default(monkeypatch):
    monkeypatch.delenv("SPOTIFY_MCP_COMMAND", raising=False)
    assert spotify_server_config() is None


def test_spotify_config_reads_command_and_args(monkeypatch):
    monkeypatch.setenv("SPOTIFY_MCP_COMMAND", "python")
    monkeypatch.setenv("SPOTIFY_MCP_ARGS", "scripts/spotify_mcp_server.py")
    config = spotify_server_config()
    assert config is not None
    assert config.command == "python"
    assert config.args == ["scripts/spotify_mcp_server.py"]
