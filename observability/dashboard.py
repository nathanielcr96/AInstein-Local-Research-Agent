"""Read-only Streamlit viewer over observability/metrics.sqlite — the
"Turns" overview page. Tool-usage charts live on their own page,
pages/1_Tool_Charts.py (Streamlit's own multipage convention: any script
under observability/pages/ shows up as a separate page automatically).

Deliberately separate from the Chainlit app (`streamlit run
observability/dashboard.py`, not wired into app.py's startup) — Chainlit is
a chat UI, not a dashboard framework, and this only ever needs to be open
when someone is actually looking at metrics.
"""

import streamlit as st

# Bare import, not `observability._shared`: Streamlit puts the entry
# script's own directory (observability/) on sys.path, not the project
# root, so a package-qualified import would fail depending on how/from
# where `streamlit run` is invoked. This also matters for pages/1_Tool_Charts.py
# (Streamlit keeps this same sys.path entry across every page, so this
# module resolves the same way from there too), which is the whole point
# of putting shared code here instead of duplicating it per page.
from _shared import METRICS_DB_PATH, load_data, render_filters

st.set_page_config(page_title="AInstein — Observability", layout="wide")
st.title("AInstein — Observability")

if not METRICS_DB_PATH.exists():
    st.info(f"No metrics yet — {METRICS_DB_PATH.name} doesn't exist. Run a few turns through the app first.")
    st.stop()

turns, tool_calls = load_data()

if turns.empty:
    st.info("metrics.sqlite exists but has no turns logged yet.")
    st.stop()

filtered = render_filters(turns)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Turns", len(filtered))
col2.metric("Avg total tokens", f"{filtered['total_tokens'].mean():,.0f}" if len(filtered) else "—")
col3.metric("Avg execution time (s)", f"{filtered['execution_time'].mean():,.1f}" if len(filtered) else "—")
col4.metric("Avg tool calls / turn", f"{filtered['tool_calls'].mean():,.1f}" if len(filtered) else "—")
col5.metric(
    "Avg tokens/sec",
    f"{filtered['tokens_per_second'].mean():,.1f}" if filtered["tokens_per_second"].notna().any() else "—"
)

st.subheader("Turns")

st.dataframe(
    filtered[
        [
            "timestamp", "thread_id", "model", "embedding_provider", "embedding_model", "temperature",
            "num_ctx", "reasoning",
            "llm_calls", "tool_calls", "input_tokens", "output_tokens", "total_tokens",
            "llm_time", "tool_time", "execution_time", "tokens_per_second",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)
st.caption(
    "num_ctx / reasoning are only recorded for turns since this tracking was added — older turns show "
    "blank rather than a guessed value."
)

with st.expander("Tool calls for the filtered turns (raw)"):
    matching_tool_calls = tool_calls[tool_calls["turn_id"].isin(filtered["id"])]
    if matching_tool_calls.empty:
        st.write("No tool calls in the current filter.")
    else:
        st.dataframe(
            matching_tool_calls[["turn_id", "tool_name", "status", "duration"]],
            use_container_width=True,
            hide_index=True,
        )

st.caption("Tool usage charts (usage counts, tool-type breakdown, success/error rate) are on the "
           "\"Tool Charts\" page in the sidebar.")
