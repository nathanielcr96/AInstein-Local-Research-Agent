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
                num_ctx INTEGER,
                reasoning INTEGER,
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
                duration REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'success'
            )
            """
        )

        # ALTER TABLE ... ADD COLUMN for a database created before these
        # columns existed — CREATE TABLE IF NOT EXISTS above is a no-op on
        # an existing file, so a pre-existing metrics.sqlite would
        # otherwise never get them. Safe to run every startup: SQLite has
        # no "ADD COLUMN IF NOT EXISTS", so this just catches and ignores
        # the "duplicate column" error on every run after the first.
        # num_ctx/reasoning are left nullable (no DEFAULT) rather than
        # backfilled with today's values — a turn logged before this
        # existed genuinely didn't record either, and a fake default would
        # misrepresent it as known when it isn't.
        for statement in (
            "ALTER TABLE tool_calls ADD COLUMN status TEXT NOT NULL DEFAULT 'success'",
            "ALTER TABLE turns ADD COLUMN num_ctx INTEGER",
            "ALTER TABLE turns ADD COLUMN reasoning INTEGER",
        ):
            try:
                await _conn.execute(statement)
                await _conn.commit()
            except aiosqlite.OperationalError:
                pass

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
    metrics: dict,
    num_ctx: int | None = None,
    reasoning: bool | None = None
) -> None:
    """
    Records one complete turn (one call to main() in app.py) along with
    every tool used during that turn. `metrics` is the conversation_metrics
    dict already built in app.py — it's reused as-is, without duplicating
    its calculation.

    `num_ctx`/`reasoning` default to None (not just left out) so a caller
    that doesn't pass them — an older test script, say — logs an honest
    "unknown" instead of silently mismatching a hardcoded default here.
    """

    conn = await _get_conn()

    cursor = await conn.execute(
        """
        INSERT INTO turns (
            thread_id, timestamp, model, embedding_provider, embedding_model,
            temperature, num_ctx, reasoning, llm_calls, tool_calls, input_tokens,
            output_tokens, total_tokens, llm_time, tool_time, execution_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            thread_id,
            datetime.now().isoformat(timespec="seconds"),
            model,
            embedding_provider,
            embedding_model,
            temperature,
            num_ctx,
            None if reasoning is None else int(reasoning),
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
            "INSERT INTO tool_calls (turn_id, tool_name, duration, status) VALUES (?, ?, ?, ?)",
            (turn_id, tool_use["tool"], tool_use["duration"], tool_use.get("status", "success"))
        )

    await conn.commit()
