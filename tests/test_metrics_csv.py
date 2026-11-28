import csv
import io

from mcp_agent.cli import aggregate_run_metrics


def test_metrics_can_be_written_as_csv():
    rows = aggregate_run_metrics(
        [{"state": {"trace": [{"tool": "drive.search_files", "status": "success", "duration_ms": 8.0}]}}]
    )
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["tool", "calls", "successes", "failures", "average_duration_ms"])
    writer.writeheader()
    writer.writerows(rows)
    assert "drive.search_files,1,1,0,8.0" in output.getvalue()
