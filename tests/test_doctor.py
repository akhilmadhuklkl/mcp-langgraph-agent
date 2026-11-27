from mcp_agent.doctor import format_checks, readiness_checks


def test_readiness_checks_do_not_expose_token(monkeypatch):
    monkeypatch.delenv("GITHUB_MCP_COMMAND", raising=False)
    monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN", "secret-token")
    output = format_checks(readiness_checks())
    assert "secret-token" not in output
    assert "Token is configured" in output


def test_format_checks_is_readable():
    output = format_checks(readiness_checks())
    assert output.startswith("MCP agent readiness:")
    assert "GitHub command" in output
    assert "Google OAuth client" in output


def test_http_server_check_validates_optional_url(monkeypatch):
    monkeypatch.setenv("MCP_HTTP_SERVER_URL", "ftp://example.test/mcp")
    output = format_checks(readiness_checks())
    assert "Streamable HTTP server: invalid" in output
    assert "URL must use http:// or https://" in output
