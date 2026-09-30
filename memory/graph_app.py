"""Standalone Streamlit app for the 3D knowledge graph — papers, authors,
and keywords/topics from memory/store/graph.sqlite (built by
`python -m memory.knowledge_graph`, see that module for how nodes/edges
get populated).

Deliberately its own app, not a page inside the observability dashboard
(observability/dashboard.py) — kept separate on request, its own server/
port/browser tab, nothing shared between the two beyond both reading from
this project's local SQLite files. Run with:
    streamlit run memory/graph_app.py --server.port 8030

Rendered with 3d-force-graph (vasturiano/3d-force-graph, three.js-based),
embedded as raw HTML/JS via Streamlit's built-in components.v1.html — not
Plotly: real orbit controls (drag to rotate, scroll to zoom) and a
physics-based layout come for free from the library. Filtering by node
type happens in-browser (checkboxes drawn inside this same HTML block)
rather than via Streamlit widgets, so toggling a type doesn't trigger a
full component reload and lose the camera's current rotation/zoom.

Deliberately does NOT import memory.knowledge_graph — that module pulls in
KeyBERT/sentence-transformers (heavy, loads torch) at import time, needed
only for *building* the graph, not for reading an already-built
graph.sqlite. The path is recomputed locally instead.
"""

import json
import sqlite3
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

GRAPH_DB_PATH = (Path(__file__).resolve().parent / "store" / "graph.sqlite").resolve()

st.set_page_config(page_title="AInstein — Knowledge Graph", layout="wide")
st.title("Knowledge graph")

if not GRAPH_DB_PATH.exists():
    st.info(
        "No knowledge graph yet — memory/store/graph.sqlite doesn't exist. Run "
        "`python -m memory.knowledge_graph` first to build it from long_term.md."
    )
    st.stop()

conn = sqlite3.connect(f"file:{GRAPH_DB_PATH}?mode=ro", uri=True)
node_rows = conn.execute("SELECT id, label, node_type FROM nodes").fetchall()
edge_rows = conn.execute("SELECT source_id, target_id, relation_type, weight FROM edges").fetchall()
conn.close()

if not node_rows:
    st.info("graph.sqlite exists but is empty. Run `python -m memory.knowledge_graph` to populate it.")
    st.stop()

st.caption(f"{len(node_rows)} nodes, {len(edge_rows)} edges.")

graph_data = {
    "nodes": [{"id": node_id, "name": label, "type": node_type} for node_id, label, node_type in node_rows],
    "links": [
        {"source": source, "target": target, "relation": relation, "weight": weight}
        for source, target, relation, weight in edge_rows
    ],
}

# Labels are paper titles, author names and keywords — text a third party controls — and this
# JSON is pasted verbatim inside a <script> block below. json.dumps doesn't escape "<", so a
# title containing "</script><script>..." ended the block early and ran as code (verified live:
# it executed on page load, no click, in an iframe that allows scripts with this app's origin).
# < / > / & are the same characters as far as JSON and JavaScript are concerned,
# but the HTML parser never sees a tag; U+2028/2029 are line terminators in older JS engines.
def _json_for_script_tag(data) -> str:
    """JSON that is safe to paste inside an inline <script> block (see the comment above).
    Kept as a plain function so tests/test_graph_app_escaping.py can extract and test it
    without running this Streamlit script."""
    return (
        json.dumps(data)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace(" ", "\\u2028")
        .replace(" ", "\\u2029")
    )


graph_json = _json_for_script_tag(graph_data)

html = f"""
<div id="graph-container" style="position:relative; width:100%; height:800px;
     background:#0b0e14; border-radius:10px; overflow:hidden;">
  <div id="controls" style="position:absolute; top:14px; left:14px; z-index:10;
       background:rgba(20,20,32,0.82); padding:12px 16px; border-radius:8px;
       font-family:-apple-system,sans-serif; font-size:13px; color:#eee;
       box-shadow:0 2px 12px rgba(0,0,0,0.4);">
    <div style="margin-bottom:8px; font-weight:600; font-size:14px;">Node types</div>
    <label style="display:block; margin-bottom:4px; cursor:pointer;">
      <input type="checkbox" class="type-toggle" value="paper" checked>
      <span style="color:#e63946;">&#9679;</span> Papers</label>
    <label style="display:block; margin-bottom:4px; cursor:pointer;">
      <input type="checkbox" class="type-toggle" value="author" checked>
      <span style="color:#457b9d;">&#9679;</span> Authors</label>
    <label style="display:block; margin-bottom:10px; cursor:pointer;">
      <input type="checkbox" class="type-toggle" value="keyword" checked>
      <span style="color:#2a9d8f;">&#9679;</span> Keywords / Topics</label>
    <input id="search-box" type="text" placeholder="Highlight a node..."
           style="width:170px; padding:5px 7px; border-radius:5px; border:1px solid #444;
                  background:#1a1d26; color:#eee; font-size:12px;">
  </div>
  <div id="node-info" style="position:absolute; bottom:14px; left:14px; z-index:10;
       background:rgba(20,20,32,0.82); padding:8px 14px; border-radius:8px;
       font-family:-apple-system,sans-serif; font-size:12px; color:#ccc; display:none;
       max-width:320px;"></div>
  <div id="graph3d" style="width:100%; height:100%;"></div>
</div>

<script src="https://unpkg.com/3d-force-graph@1"></script>
<script>
(function() {{
  const rawData = {graph_json};
  const colorByType = {{paper: "#e63946", author: "#457b9d", keyword: "#2a9d8f"}};
  const infoBox = document.getElementById('node-info');

  function degreeOf(nodeId, links) {{
    let n = 0;
    for (const l of links) {{
      const s = (l.source && l.source.id) || l.source;
      const t = (l.target && l.target.id) || l.target;
      if (s === nodeId || t === nodeId) n++;
    }}
    return n;
  }}

  // 3d-force-graph renders nodeLabel as HTML, and the info box below is built with innerHTML —
  // both take node names straight from paper metadata, so they must be escaped.
  const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');

  window._debugGraph = null;
  // preserveDrawingBuffer: without it, the WebGL context clears its drawing
  // buffer right after each render, so canvas.toDataURL()/drawImage() called
  // from outside the render loop (e.g. to record a demo GIF) captures a
  // blank black frame almost every time — verified live, needed to record
  // a screen-capture GIF of this page.
  const Graph = ForceGraph3D({{ rendererConfig: {{ preserveDrawingBuffer: true }} }})(document.getElementById('graph3d'))
    .graphData(rawData)
    .backgroundColor("#0b0e14")
    .showNavInfo(false)
    .nodeLabel(n => `${{esc(n.name)}} (${{esc(n.type)}})`)
    .nodeColor(n => colorByType[n.type] || "#999999")
    .nodeVal(n => 1 + Math.min(10, degreeOf(n.id, rawData.links)))
    .nodeResolution(12)
    .linkColor(() => "rgba(255,255,255,0.18)")
    .linkOpacity(0.5)
    .linkWidth(l => Math.max(0.4, (l.weight || 1) * 1.1))
    .linkDirectionalParticles(l => l.relation === "cites" ? 2 : 0)
    .linkDirectionalParticleWidth(1.4)
    ;
  window._debugGraph = Graph;
  Graph
    .onNodeClick(node => {{
      const distance = 90;
      const distRatio = 1 + distance / Math.hypot(node.x || 1, node.y || 1, node.z || 1);
      Graph.cameraPosition(
        {{ x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }},
        node,
        900
      );
      infoBox.style.display = 'block';
      infoBox.innerHTML = `<b>${{esc(node.name)}}</b><br>type: ${{esc(node.type)}}<br>connections: ${{degreeOf(node.id, rawData.links)}}`;
    }});

  // The library's own zoomToFit() was tried here first and, with a few
  // hundred nodes, ended up parking the camera at ~17x the graph's actual
  // radius (a real bug hit live: node coordinates spanned roughly ±85 on
  // each axis, but zoomToFit(400, 60) positioned the camera at z=1474,
  // rendering the whole graph as a near-invisible speck in one corner).
  // Computing the distance directly from the actual node positions
  // instead is simple and gives a predictable, correct result regardless
  // of graph size.
  function fitCameraToNodes() {{
    const nodes = Graph.graphData().nodes;
    let maxDist = 50;
    for (const n of nodes) {{
      const d = Math.hypot(n.x || 0, n.y || 0, n.z || 0);
      if (d > maxDist) maxDist = d;
    }}
    const camDist = maxDist * 2.2;
    // The 3-arg form (pos, lookAt, transitionMs) silently failed to apply
    // at all in testing — cameraPosition() kept reporting the untouched
    // default afterward. The plain 1-arg instant-set form verified live
    // to actually work; no animated transition, but a reliable snap beats
    // a call that quietly does nothing.
    Graph.cameraPosition({{ x: 0, y: 0, z: camDist }});
  }}
  // A few hundred nodes keep drifting apart for several seconds — a graph
  // spanning roughly ±85 on each axis at t=1.5s had spread to ±275 by
  // t=6s in testing, so fitting the camera once (even a few seconds in)
  // still goes stale almost immediately as the layout keeps expanding.
  // Re-fitting on an interval while the simulation is still active tracks
  // that expansion instead of freezing on a snapshot of it; each call
  // re-measures current node positions, so it stays correct once the
  // layout actually settles down instead of overshooting further.
  let refitCount = 0;
  const refitInterval = setInterval(() => {{
    fitCameraToNodes();
    refitCount++;
    if (refitCount >= 12) clearInterval(refitInterval);  // ~12s of tracking, then leave the camera alone
  }}, 1000);

  document.querySelectorAll('.type-toggle').forEach(cb => {{
    cb.addEventListener('change', () => {{
      const active = Array.from(document.querySelectorAll('.type-toggle:checked')).map(c => c.value);
      const filteredNodes = rawData.nodes.filter(n => active.includes(n.type));
      const idSet = new Set(filteredNodes.map(n => n.id));
      const filteredLinks = rawData.links.filter(l => {{
        const s = (l.source && l.source.id) || l.source;
        const t = (l.target && l.target.id) || l.target;
        return idSet.has(s) && idSet.has(t);
      }});
      Graph.graphData({{nodes: filteredNodes, links: filteredLinks}});
    }});
  }});

  document.getElementById('search-box').addEventListener('input', (e) => {{
    const q = e.target.value.toLowerCase().trim();
    if (!q) {{
      Graph.nodeColor(n => colorByType[n.type] || "#999999");
      return;
    }}
    Graph.nodeColor(n => n.name.toLowerCase().includes(q) ? "#ffd60a" : "rgba(120,120,130,0.25)");
  }});
}})();
</script>
"""

components.html(html, height=820, scrolling=False)

st.caption(
    "Drag to rotate, scroll to zoom, click a node to focus the camera on it and see its details "
    "bottom-left. The panel top-left hides node types or highlights matches by name. Node size "
    "reflects how many connections it has."
)
