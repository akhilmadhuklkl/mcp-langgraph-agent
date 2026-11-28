from mcp_agent.auth import authorize, configured_api_key


def test_authorize_requires_a_key(monkeypatch):
    monkeypatch.delenv("MCP_AGENT_API_KEY", raising=False)
    assert not authorize("secret")


def test_authorize_accepts_only_matching_key():
    assert authorize("secret", "secret")
    assert not authorize("wrong", "secret")
    assert not authorize(None, "secret")


def test_configured_key_is_optional_and_trimmed(monkeypatch):
    monkeypatch.setenv("MCP_AGENT_API_KEY", "  local-secret  ")
    assert configured_api_key() == "local-secret"
