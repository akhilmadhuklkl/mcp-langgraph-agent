import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4


class RunStore:
    """Small SQLite store for resumable agent run state."""

    def __init__(self, path: str | Path = "data/agent_runs.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_runs (
                    run_id TEXT PRIMARY KEY,
                    request TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def create(self, request: str, state: dict[str, Any]) -> str:
        run_id = str(uuid4())
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO agent_runs (run_id, request, state_json) VALUES (?, ?, ?)",
                (run_id, request, json.dumps(state, default=str)),
            )
        return run_id

    def save(self, run_id: str, state: dict[str, Any]) -> None:
        with self._connection() as connection:
            connection.execute(
                "UPDATE agent_runs SET state_json = ?, updated_at = CURRENT_TIMESTAMP WHERE run_id = ?",
                (json.dumps(state, default=str), run_id),
            )

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT state_json FROM agent_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return json.loads(row[0]) if row else None
