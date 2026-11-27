from mcp_agent.mcp_client import MCPToolRegistry


def test_metrics_aggregate_calls_retries_and_latency():
    registry = MCPToolRegistry()
    registry._record_metric("github.search_issues", 0, 2, success=True)
    registry._record_metric("github.search_issues", 0, 1, success=False)

    metrics = registry.metrics()

    assert metrics[0]["tool"] == "github.search_issues"
    assert metrics[0]["calls"] == 2
    assert metrics[0]["successes"] == 1
    assert metrics[0]["failures"] == 1
    assert metrics[0]["retries"] == 1
    assert metrics[0]["average_duration_ms"] >= 0
