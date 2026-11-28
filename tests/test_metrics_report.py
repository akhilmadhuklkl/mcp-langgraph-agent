from mcp_agent.cli import aggregate_run_metrics


def test_aggregate_run_metrics_groups_trace_items():
    runs = [
        {"state": {"trace": [{"tool": "gmail.search_threads", "status": "success", "duration_ms": 10.0}]}},
        {"state": {"trace": [{"tool": "gmail.search_threads", "status": "error", "duration_ms": 20.0}]}},
    ]

    assert aggregate_run_metrics(runs) == [
        {
            "tool": "gmail.search_threads",
            "calls": 2,
            "successes": 1,
            "failures": 1,
            "average_duration_ms": 15.0,
        }
    ]
