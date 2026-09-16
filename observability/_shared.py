"""Shared data-loading and filtering code for the observability pages
(dashboard.py and pages/1_Tool_Charts.py). Kept in one place so both pages
apply the exact same filter logic instead of two copies drifting apart.

Not itself a Streamlit page — the leading underscore keeps Streamlit's
`pages/` auto-discovery from ever picking it up as one.
"""

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

METRICS_DB_PATH = (Path(__file__).parent / "metrics.sqlite").resolve()


@st.cache_data(ttl=10)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    conn = sqlite3.connect(f"file:{METRICS_DB_PATH}?mode=ro", uri=True)
    conn.execute("PRAGMA busy_timeout = 15000")
    try:
        turns = pd.read_sql_query("SELECT * FROM turns ORDER BY id DESC", conn)
        tool_calls = pd.read_sql_query("SELECT * FROM tool_calls", conn)
    finally:
        conn.close()
    turns["timestamp"] = pd.to_datetime(turns["timestamp"])

    # Local models have no per-token dollar cost, so the metric that
    # actually matters for comparing them is speed, not spend — tokens/sec
    # as a throughput proxy. Computed once here (not per page) so every
    # page that reads `turns` gets it for free. `.replace(0, pd.NA)` avoids
    # a division-by-zero turning into `inf` for the rare turn with
    # execution_time == 0 (no LLM/tool calls at all) — NaN is skipped by
    # `.mean()` by default, `inf` would silently poison it instead.
    turns["tokens_per_second"] = turns["total_tokens"] / turns["execution_time"].replace(0, pd.NA)

    return turns, tool_calls


def render_filters(turns: pd.DataFrame) -> pd.DataFrame:
    """Renders the standard sidebar filter set and returns the filtered
    `turns` DataFrame. Each page calls this on its own — Streamlit reruns
    one page's script per interaction, so there's no shared widget state to
    coordinate between pages, and every page gets the same filters over
    whatever it's showing (the turns table here, tool-call charts there).
    """

    st.sidebar.header("Filters")

    models = st.sidebar.multiselect("Model", sorted(turns["model"].dropna().unique()))
    embedding_providers = st.sidebar.multiselect(
        "Embedding provider", sorted(turns["embedding_provider"].dropna().unique())
    )
    thread_id_search = st.sidebar.text_input("Thread ID contains")

    min_date, max_date = turns["timestamp"].min().date(), turns["timestamp"].max().date()
    date_range = st.sidebar.date_input(
        "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )

    filtered = turns.copy()

    if models:
        filtered = filtered[filtered["model"].isin(models)]
    if embedding_providers:
        filtered = filtered[filtered["embedding_provider"].isin(embedding_providers)]
    if thread_id_search:
        filtered = filtered[filtered["thread_id"].str.contains(thread_id_search, case=False, na=False)]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        filtered = filtered[(filtered["timestamp"].dt.date >= start) & (filtered["timestamp"].dt.date <= end)]

    st.caption(f"{len(filtered)} of {len(turns)} turns match the current filters.")

    return filtered
