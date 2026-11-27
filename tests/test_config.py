from mcp_agent.config import github_server_config


def test_github_config_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("GITHUB_MCP_COMMAND", raising=False)
    assert github_server_config() is None


def test_github_config_reads_stdio_settings(monkeypatch):
    monkeypatch.setenv("GITHUB_MCP_COMMAND", "github-mcp-server")
    monkeypatch.setenv("GITHUB_MCP_ARGS", "stdio --toolsets repos,issues")
    config = github_server_config()
    assert config is not None
    assert config.command == "github-mcp-server"
    assert config.args == ["stdio", "--toolsets", "repos,issues"]
