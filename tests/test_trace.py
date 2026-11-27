from mcp_agent.trace import format_trace, redact_arguments


def test_redact_arguments_hides_sensitive_fields():
    assert redact_arguments({"query": "MCP", "body": "private", "token": "secret"}) == {
        "query": "MCP",
        "body": "[REDACTED]",
        "token": "[REDACTED]",
    }


def test_redact_arguments_recurses_into_nested_values():
    result = redact_arguments({"message": {"content": "private", "parts": [{"token": "secret"}]}})
    assert result == {"message": {"content": "[REDACTED]", "parts": [{"token": "[REDACTED]"}]}}


def test_formats_successful_trace():
    output = format_trace([
        {
            "tool": "github.search_issues",
            "arguments": {"query": "open"},
            "status": "success",
            "duration_ms": 12.5,
        }
    ])
    assert "Execution trace:" in output
    assert "github.search_issues" in output
    assert "status=success" in output
    assert "duration=12.50ms" in output


def test_formats_error_trace():
    output = format_trace([
        {
            "tool": "gmail.search_emails",
            "arguments": {"query": "MCP"},
            "status": "error",
            "duration_ms": 4.0,
            "error": "server unavailable",
        }
    ])
    assert "status=error" in output
    assert "server unavailable" in output
