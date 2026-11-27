from mcp_agent.config import gmail_server_config


def test_gmail_config_is_mock_by_default(monkeypatch):
    monkeypatch.delenv("GMAIL_MCP_COMMAND", raising=False)
    assert gmail_server_config() is None


def test_gmail_config_reads_command_and_args(monkeypatch):
    monkeypatch.setenv("GMAIL_MCP_COMMAND", "gmail-mcp-server")
    monkeypatch.setenv("GMAIL_MCP_ARGS", "stdio --account personal")
    config = gmail_server_config()
    assert config is not None
    assert config.command == "gmail-mcp-server"
    assert config.args == ["stdio", "--account", "personal"]
