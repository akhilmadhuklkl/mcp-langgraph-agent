from mcp_agent.config import drive_server_config


def test_drive_config_is_mock_by_default(monkeypatch):
    monkeypatch.delenv("GOOGLE_DRIVE_MCP_COMMAND", raising=False)
    assert drive_server_config() is None


def test_drive_config_reads_command_and_args(monkeypatch):
    monkeypatch.setenv("GOOGLE_DRIVE_MCP_COMMAND", "drive-mcp-server")
    monkeypatch.setenv("GOOGLE_DRIVE_MCP_ARGS", "stdio --account personal")
    config = drive_server_config()
    assert config is not None
    assert config.command == "drive-mcp-server"
    assert config.args == ["stdio", "--account", "personal"]
