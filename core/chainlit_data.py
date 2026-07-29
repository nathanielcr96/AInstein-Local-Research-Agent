import sqlite3
from pathlib import Path

import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

# core/chainlit_data.py -> parent is core/, parent.parent is the project
# root, where checkpoints.sqlite already lives — chainlit_data.sqlite sits
# next to it, same convention.
PROJECT_DIR = Path(__file__).parent.parent.resolve()
CHAINLIT_DATA_DB_PATH = PROJECT_DIR / "chainlit_data.sqlite"

# SQLAlchemyDataLayer expects these five tables to already exist — it never
# creates them itself. Chainlit's own docs only give a Postgres schema
# (UUID/JSONB/TEXT[] types); this is the SQLite equivalent, reverse
# engineered against the authoritative field lists in chainlit/step.py
# (StepDict), chainlit/element.py (ElementDict), chainlit/types.py
# (ThreadDict, Feedback) — the queries in chainlit/data/sql_alchemy.py build
# their column list dynamically from whatever fields are present on the
# object being saved, so those TypedDict/dataclass definitions are the real
# source of truth, not any single query. JSON-ish columns
# (metadata/tags/props/generation/modes) are stored as TEXT — the data layer
# already json.dumps/json.loads them itself for SQLite compatibility.
_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    identifier TEXT NOT NULL UNIQUE,
    metadata TEXT NOT NULL DEFAULT '{}',
    createdAt TEXT
);

CREATE TABLE IF NOT EXISTS threads (
    id TEXT PRIMARY KEY,
    createdAt TEXT,
    name TEXT,
    userId TEXT REFERENCES users(id),
    userIdentifier TEXT,
    tags TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS steps (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    threadId TEXT NOT NULL REFERENCES threads(id),
    parentId TEXT,
    command TEXT,
    modes TEXT,
    streaming INTEGER NOT NULL DEFAULT 0,
    waitForAnswer INTEGER,
    isError INTEGER,
    metadata TEXT,
    tags TEXT,
    input TEXT,
    output TEXT,
    createdAt TEXT,
    start TEXT,
    "end" TEXT,
    generation TEXT,
    showInput TEXT,
    defaultOpen INTEGER,
    autoCollapse INTEGER,
    language TEXT,
    icon TEXT
);

CREATE TABLE IF NOT EXISTS elements (
    id TEXT PRIMARY KEY,
    threadId TEXT REFERENCES threads(id),
    type TEXT,
    chainlitKey TEXT,
    url TEXT,
    objectKey TEXT,
    name TEXT,
    display TEXT,
    size TEXT,
    language TEXT,
    page INTEGER,
    props TEXT,
    autoPlay INTEGER,
    playerConfig TEXT,
    forId TEXT,
    mime TEXT
);

CREATE TABLE IF NOT EXISTS feedbacks (
    id TEXT PRIMARY KEY,
    forId TEXT NOT NULL,
    threadId TEXT,
    value INTEGER NOT NULL,
    comment TEXT
);

CREATE INDEX IF NOT EXISTS idx_threads_userId ON threads(userId);
CREATE INDEX IF NOT EXISTS idx_steps_threadId ON steps(threadId);
CREATE INDEX IF NOT EXISTS idx_elements_threadId ON elements(threadId);
CREATE INDEX IF NOT EXISTS idx_feedbacks_forId ON feedbacks(forId);
"""

_schema_ready = False

def _ensure_schema() -> None:
    global _schema_ready

    if _schema_ready:
        return

    conn = sqlite3.connect(str(CHAINLIT_DATA_DB_PATH))

    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()

    _schema_ready = True

def build_data_layer() -> SQLAlchemyDataLayer:
    """
    Factory registered via cl.data_layer(build_data_layer) in app.py.
    Called lazily by chainlit itself, so the schema only needs to exist by
    the time the first session connects, not at import time.
    """
    _ensure_schema()
    return SQLAlchemyDataLayer(conninfo=f"sqlite+aiosqlite:///{CHAINLIT_DATA_DB_PATH}")

# This app has exactly one local user, and no reverse proxy in front of it
# to assert identity via real headers — header_auth_callback is used here
# only because Chainlit hard-requires *some* auth mechanism to be present
# for the thread-history sidebar and resume feature to work at all
# (/project/threads returns 401 without a current_user). Returning the same
# fixed identity unconditionally means there is no login page, no password,
# no visible friction: every session is silently "logged in" as the same
# local user and sees the same thread history.
async def authenticate_local_user(headers) -> cl.User:
    return cl.User(identifier="local")
