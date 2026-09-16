"""Model & configuration comparison — grouped aggregates side by side,
instead of the one-at-a-time view Turns/Tool Charts give you through their
own filters (pick a model, look, change the filter, look again).

Two comparisons, same shape: by `model`, and by `reasoning` (True/False).
The latter only has real data going forward — see graph.py's build_agent
and app.py, where `reasoning` became an actual observable parameter
instead of a literal buried inside a ChatOllama(...) call — so this page
is what finally lets a `reasoning=True` vs `False` question get answered
from real numbers instead of manual test notes.
"""

import altair as alt
import pandas as pd
import streamlit as st

from _shared import METRICS_DB_PATH, load_data, render_filters

st.set_page_config(page_title="AInstein — Model Comparison", layout="wide")
st.title("Model comparison")

if not METRICS_DB_PATH.exists():
    st.info(f"No metrics yet — {METRICS_DB_PATH.name} doesn't exist. Run a few turns through the app first.")
    st.stop()

turns, tool_calls = load_data()

if turns.empty:
    st.info("metrics.sqlite exists but has no turns logged yet.")
    st.stop()

filtered = render_filters(turns)

if filtered.empty:
    st.info("No turns match the current filters.")
    st.stop()

# (column, display label) — reused for both the by-model and by-reasoning
# sections so the two stay visually consistent.
_METRICS = [
    ("total_tokens", "Avg total tokens"),
    ("execution_time", "Avg execution time (s)"),
    ("tokens_per_second", "Avg tokens/sec"),
    ("tool_calls", "Avg tool calls / turn"),
]


def _grouped_bar(df: pd.DataFrame, group_col: str, value_col: str, title: str):
    agg = df.groupby(group_col)[value_col].mean().reset_index().dropna(subset=[value_col])
    if agg.empty:
        return None
    return (
        alt.Chart(agg)
        .mark_bar()
        .encode(
            x=alt.X(f"{value_col}:Q", title=title),
            y=alt.Y(f"{group_col}:N", sort="-x", title=None),
            tooltip=[group_col, alt.Tooltip(f"{value_col}:Q", format=",.1f", title=title)],
        )
        .properties(height=max(120, 40 * agg[group_col].nunique()))
    )


def _render_comparison(df: pd.DataFrame, group_col: str):
    summary = df.groupby(group_col).agg(
        turns=("id", "count"),
        **{label: (col, "mean") for col, label in _METRICS},
    ).reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)

    cols = st.columns(2)
    for i, (col_key, label) in enumerate(_METRICS):
        chart = _grouped_bar(df, group_col, col_key, label)
        with cols[i % 2]:
            st.caption(label)
            if chart is None:
                st.write("No data for this metric in the current filter.")
            else:
                st.altair_chart(chart, use_container_width=True)


st.subheader("By model")
_render_comparison(filtered, "model")

st.divider()
st.subheader("By reasoning setting")

with_reasoning = filtered.dropna(subset=["reasoning"]).copy()

if with_reasoning.empty:
    st.info(
        "No turns with a recorded `reasoning` value in the current filter — this only started being "
        "tracked recently, so turns logged before that show blank rather than a guessed value. Run a "
        "few more turns (ideally some with reasoning on and some off) to populate this comparison."
    )
else:
    with_reasoning["reasoning"] = with_reasoning["reasoning"].map({0: "False", 1: "True"})
    _render_comparison(with_reasoning, "reasoning")
