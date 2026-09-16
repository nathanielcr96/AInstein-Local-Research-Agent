"""Activity over time — how many model calls/turns happened, bucketed by
day or hour, over whatever date range is picked in the sidebar filter
(shared with the other pages via _shared.render_filters, so changing the
date range here works exactly like it does everywhere else in this
dashboard — no separate date control to keep in sync).
"""

import altair as alt
import streamlit as st

from _shared import METRICS_DB_PATH, load_data, render_filters

st.set_page_config(page_title="AInstein — Activity Over Time", layout="wide")
st.title("Activity over time")

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

granularity = st.radio("Bucket size", ["Day", "Hour"], horizontal=True)
freq = "D" if granularity == "Day" else "h"

filtered = filtered.copy()
filtered["bucket"] = filtered["timestamp"].dt.floor(freq)

st.subheader("Model (LLM) calls over time")

by_bucket = filtered.groupby("bucket").agg(
    llm_calls=("llm_calls", "sum"),
    turns=("id", "count"),
).reset_index()

st.altair_chart(
    alt.Chart(by_bucket)
    .mark_line(point=True)
    .encode(
        x=alt.X("bucket:T", title=granularity),
        y=alt.Y("llm_calls:Q", title="LLM calls"),
        tooltip=[alt.Tooltip("bucket:T", title=granularity), "llm_calls", "turns"],
    )
    .properties(height=300),
    use_container_width=True,
)

st.subheader("Turns over time, by model")

by_bucket_model = filtered.groupby(["bucket", "model"]).size().reset_index(name="turns")

st.altair_chart(
    alt.Chart(by_bucket_model)
    .mark_bar()
    .encode(
        x=alt.X("bucket:T", title=granularity),
        y=alt.Y("turns:Q", title="Turns"),
        color=alt.Color("model:N", title="Model"),
        tooltip=[alt.Tooltip("bucket:T", title=granularity), "model", "turns"],
    )
    .properties(height=300),
    use_container_width=True,
)

st.caption(
    "Both charts follow the date range and other filters in the sidebar — narrow the range and switch "
    "to \"Hour\" buckets to zoom into a single busy day, or widen it and use \"Day\" buckets to see "
    "activity across weeks."
)
