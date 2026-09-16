"""Tool-usage charts — a separate Streamlit page from the main "Turns"
overview (observability/dashboard.py). Auto-discovered by Streamlit's own
multipage convention (any script under observability/pages/ becomes a page
in the sidebar nav); this file's own sidebar filters are independent from
the main page's — each Streamlit page reruns its own script, so filter
state isn't shared automatically, and re-rendering the same filter set
here (via _shared.render_filters) keeps both pages consistent without
duplicating the filtering logic itself.
"""

import altair as alt
import streamlit as st

from _shared import METRICS_DB_PATH, load_data, render_filters

# Stable color per status so the same status always reads as the same
# color across charts, instead of Altair picking an arbitrary one per
# render.
_STATUS_COLORS = {
    "success": "#2ca02c",
    "error": "#d62728",
    "rate_limited": "#ff7f0e",
    "timeout": "#ff7f0e",
}

st.set_page_config(page_title="AInstein — Tool Charts", layout="wide")
st.title("Tool usage")

if not METRICS_DB_PATH.exists():
    st.info(f"No metrics yet — {METRICS_DB_PATH.name} doesn't exist. Run a few turns through the app first.")
    st.stop()

turns, tool_calls = load_data()

if turns.empty:
    st.info("metrics.sqlite exists but has no turns logged yet.")
    st.stop()

filtered = render_filters(turns)

matching_tool_calls = tool_calls[tool_calls["turn_id"].isin(filtered["id"])]

if matching_tool_calls.empty:
    st.write("No tool calls in the current filter.")
    st.stop()

chart_col1, chart_col2 = st.columns(2)

counts_by_tool = matching_tool_calls.groupby("tool_name").size().reset_index(name="calls")

with chart_col1:
    st.subheader("Calls per tool")
    st.altair_chart(
        alt.Chart(counts_by_tool)
        .mark_bar()
        .encode(
            x=alt.X("calls:Q", title="Calls"),
            y=alt.Y("tool_name:N", sort="-x", title="Tool"),
            tooltip=["tool_name", "calls"],
        )
        .properties(height=max(200, 28 * len(counts_by_tool))),
        use_container_width=True,
    )

with chart_col2:
    st.subheader("Tool-type breakdown")
    st.altair_chart(
        alt.Chart(counts_by_tool)
        .mark_arc()
        .encode(
            theta="calls:Q",
            color=alt.Color("tool_name:N", title="Tool"),
            tooltip=["tool_name", "calls"],
        )
        .properties(height=max(200, 28 * len(counts_by_tool))),
        use_container_width=True,
    )

st.subheader("Success / error breakdown per tool")

counts_by_tool_status = (
    matching_tool_calls.groupby(["tool_name", "status"]).size().reset_index(name="calls")
)

st.altair_chart(
    alt.Chart(counts_by_tool_status)
    .mark_bar()
    .encode(
        x=alt.X("calls:Q", title="Calls"),
        y=alt.Y("tool_name:N", sort="-x", title="Tool"),
        color=alt.Color(
            "status:N",
            title="Status",
            scale=alt.Scale(domain=list(_STATUS_COLORS.keys()), range=list(_STATUS_COLORS.values())),
        ),
        order=alt.Order("status:N"),
        tooltip=["tool_name", "status", "calls"],
    )
    .properties(height=max(200, 28 * counts_by_tool_status["tool_name"].nunique())),
    use_container_width=True,
)

st.caption(
    "Status comes from each tool's own reported outcome (a ToolMessage marked \"error\", or a "
    "\"status\" field in its JSON output — e.g. \"rate_limited\" from citation_graph/search_papers). "
    "A call that never finishes at all — the agent hangs mid-tool-call — produces no row here, since "
    "it's only logged once the turn completes; that failure mode isn't visible in this chart."
)

with st.expander("Tool calls for the filtered turns (raw)"):
    st.dataframe(
        matching_tool_calls[["turn_id", "tool_name", "status", "duration"]],
        use_container_width=True,
        hide_index=True,
    )
