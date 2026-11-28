from mcp_agent.cli import render_metrics_html


def test_metrics_html_is_self_contained():
    html = render_metrics_html(
        [{"tool": "gmail.search_threads", "calls": 1, "successes": 1, "failures": 0, "average_duration_ms": 4.5}]
    )
    assert "<title>MCP Agent Metrics</title>" in html
    assert "gmail.search_threads" in html
    assert "<table>" in html


def test_metrics_html_escapes_tool_names():
    html = render_metrics_html(
        [{"tool": "<script>alert(1)</script>", "calls": 1, "successes": 1, "failures": 0, "average_duration_ms": 1.0}]
    )
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
