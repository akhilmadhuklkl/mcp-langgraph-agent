from pathlib import Path
from uuid import uuid4

from mcp_agent.persistence import RunStore


def test_recent_runs_returns_saved_runs():
    path = Path("data") / f"test-{uuid4()}.db"
    store = RunStore(path)
    store.create("First", {"approval_status": "not_required"})
    store.create("Second", {"approval_status": "pending"})
    items = store.recent(10)
    assert len(items) == 2
    assert {item["request"] for item in items} == {"First", "Second"}
    path.unlink(missing_ok=True)
