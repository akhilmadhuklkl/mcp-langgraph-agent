from mcp_agent.planner import ollama_settings


def test_ollama_settings_are_optional(monkeypatch):
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    assert ollama_settings() is None


def test_ollama_settings_use_configured_model_and_default_url(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    assert ollama_settings() == ("llama3.2:3b", "http://127.0.0.1:11434/v1")


def test_ollama_settings_use_custom_url(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11435/v1")
    assert ollama_settings() == ("llama3.2:3b", "http://127.0.0.1:11435/v1")
