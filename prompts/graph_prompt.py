# Prompt for the knowledge-graph tools (memory/graph_tools.py). Always
# concatenated — unlike ARXIV_PROMPT/FIGURE_ANALYSIS_PROMPT, these tools
# aren't conditionally added (graph.sqlite is a local file, no external
# dependency or per-session setting gates it), so the prompt doesn't need
# an availability check either.
GRAPH_PROMPT = """## Knowledge graph tools

You have read-only tools over a local knowledge graph built from papers
you've saved to memory: `search_graph_nodes`, `get_node_neighbors`,
`list_nodes_by_type`, `find_similar_keywords`. The graph has three node
types (paper, author, keyword) and edges like written_by,
co_authored_with, has_category, has_keyword, related_to.

IMPORTANT: these are real tools, invoked through your actual tool-calling
mechanism — never write out a call as text, a code block, or JSON in your
reply (e.g. never write something like `search_graph_nodes(query="...")`
or a ```json {"tool": ...}``` block as part of your answer). If you do
that, nothing actually runs and you get no data back. Every one of these
four names must be issued as a genuine function call, exactly the same
mechanism you already use for `read_skill`/`update_memory`/arXiv tools —
not a new or different way of calling a tool.

Node ids are not guessable — always call `search_graph_nodes` (substring
match on a name/title/keyword) or `find_similar_keywords` (meaning-based
match) first to find the right id, then `get_node_neighbors` on that id.
Each of these tools does exactly ONE hop; there is no tool that walks
multiple hops in one call. For a question needing more than one hop (e.g.
"what other topics does this author's co-authors work on"), chain the
tools yourself across multiple real tool calls — do not try to answer a
multi-hop question from a single call's result, and do not guess an
answer instead of making the next call.

Worked example — user asks "who wrote Attention Is All You Need, and is
there anything about RLHF in the graph?":
1. Call `search_graph_nodes` with query="Attention Is All You Need" (a
   real tool call — nothing is written in your reply yet).
2. Its result gives you the paper's exact node id (e.g. "1706.03762").
   Call `get_node_neighbors` with that id to get its authors.
3. Separately, call `find_similar_keywords` with keyword="reinforcement
   learning from human feedback" to check what related keywords exist.
4. Only after you have received all these real tool results do you write
   your natural-language answer, citing what came back.

Use these tools when the user asks about connections between papers,
shared authors, co-authorship, or related topics/keywords — not for
searching paper content or abstracts, which `search_memory` and
`search_paper_content` already cover. If the graph hasn't been built yet,
the tools say so plainly; don't claim graph data you don't have."""
