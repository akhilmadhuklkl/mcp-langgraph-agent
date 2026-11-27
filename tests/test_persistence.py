from mcp_agent.persistence import RunStore
from pathlib import Path
from uuid import uuid4


def test_run_store_round_trip():
    path = Path("data") / f"test-{uuid4()}.db"
    store = RunStore(path)
    run_id = store.create("Search GitHub", {"request": "Search GitHub", "plan": []})
    store.save(run_id, {"request": "Search GitHub", "plan": [{"tool": "github.search_issues"}]})
    saved = store.get(run_id)
    assert saved is not None
    assert saved["plan"][0]["tool"] == "github.search_issues"
    path.unlink(missing_ok=True)


def test_missing_run_returns_none():
    path = Path("data") / f"test-{uuid4()}.db"
    assert RunStore(path).get("missing") is None
    path.unlink(missing_ok=True)
