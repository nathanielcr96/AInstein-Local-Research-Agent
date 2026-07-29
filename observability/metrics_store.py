from datetime import datetime
from pathlib import Path

import aiosqlite

# Same as checkpoints.sqlite: a lazy async resource, can't be opened at
# module import time (synchronous code). metrics.sqlite lives alongside
# this package's code, not at the project root — everything related to
# observability stays together, same as memory/.
METRICS_DB_PATH = (Path(__file__).parent / "metrics.sqlite").resolve()

_conn: aiosqlite.Connection | None = None

async def _get_conn() -> aiosqlite.Connection:

    global _conn

    if _conn is None:

        _conn = await aiosqlite.connect(str(METRICS_DB_PATH))

        await _conn.execute(
            """
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                model TEXT,
                embedding_provider TEXT,
                embedding_model TEXT,
                temperature REAL,
                llm_calls INTEGER,
                tool_calls INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER,
                llm_time REAL,
                tool_time REAL,
                execution_time REAL
            )
            """
        )

        await _conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                turn_id INTEGER NOT NULL REFERENCES turns(id),
                tool_name TEXT NOT NULL,
                duration REAL NOT NULL
            )
            """
        )

        await _conn.execute("CREATE INDEX IF NOT EXISTS idx_turns_thread_id ON turns(thread_id)")
        await _conn.execute("CREATE INDEX IF NOT EXISTS idx_tool_calls_turn_id ON tool_calls(turn_id)")

        await _conn.commit()

    return _conn

async def log_turn(
    *,
    thread_id: str,
    model: str,
    embedding_provider: str | None,
    embedding_model: str | None,
    temperature: float,
    metrics: dict
) -> None:
    """
    Records one complete turn (one call to main() in app.py) along with
    every tool used during that turn. `metrics` is the conversation_metrics
    dict already built in app.py — it's reused as-is, without duplicating
    its calculation.
    """

    conn = await _get_conn()

    cursor = await conn.execute(
        """
        INSERT INTO turns (
            thread_id, timestamp, model, embedding_provider, embedding_model,
            temperature, llm_calls, tool_calls, input_tokens, output_tokens,
            total_tokens, llm_time, tool_time, execution_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            thread_id,
            datetime.now().isoformat(timespec="seconds"),
            model,
            embedding_provider,
            embedding_model,
            temperature,
            metrics["llm_calls"],
            metrics["tool_calls"],
            metrics["input_tokens"],
            metrics["output_tokens"],
            metrics["total_tokens"],
            metrics["llm_time"],
            metrics["tool_time"],
            metrics["execution_time"]
        )
    )

    turn_id = cursor.lastrowid

    for tool_use in metrics.get("tools_used", []):

        await conn.execute(
            "INSERT INTO tool_calls (turn_id, tool_name, duration) VALUES (?, ?, ?)",
            (turn_id, tool_use["tool"], tool_use["duration"])
        )

    await conn.commit()
