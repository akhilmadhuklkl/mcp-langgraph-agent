from mcp_agent.persistence import RunStore


def test_run_store_round_trip(tmp_path):
    store = RunStore(tmp_path / "runs.db")
    run_id = store.create("Search GitHub", {"request": "Search GitHub", "plan": []})
    store.save(run_id, {"request": "Search GitHub", "plan": [{"tool": "github.search_issues"}]})
    saved = store.get(run_id)
    assert saved is not None
    assert saved["plan"][0]["tool"] == "github.search_issues"


def test_missing_run_returns_none(tmp_path):
    assert RunStore(tmp_path / "runs.db").get("missing") is None
