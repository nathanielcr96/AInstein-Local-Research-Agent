---
name: knowledge-graph
description: How to query the local knowledge graph of papers/authors/keywords with search_graph_nodes, get_node_neighbors, list_nodes_by_type, find_similar_keywords. Use whenever the user asks about connections between papers, shared authors, co-authorship, related topics/keywords, or explicitly mentions "the graph"/"el grafo"/"knowledge graph" — not for searching paper content or abstracts (search_memory/search_paper_content cover that).
---

# Knowledge graph tools

Four read-only tools over a local graph built from papers saved to memory (`memory/store/graph.sqlite`): `search_graph_nodes`, `get_node_neighbors`, `list_nodes_by_type`, `find_similar_keywords`. Three node types (paper, author, keyword); edge types written_by, co_authored_with, has_category, has_keyword, related_to.

**These are real tools, invoked through your actual tool-calling mechanism — never written out as text, a code block, or JSON in your reply.** Verified live, repeatedly, that this exact failure happens: writing `search_graph_nodes(query="...")` as plain text, or inside a single backtick, or inside a triple-backtick fence, or as a `{"tool": ...}` JSON blob — all of these do NOT execute anything. If you do any of that, no data comes back, and going on to answer anyway means either an empty answer or (worse) inventing plausible-sounding fake results — never do that; a graph question you cannot actually query is a "let me check that" you must resolve with a real call, not a guess dressed up as an answer.

**Do not do any of these — each one has actually happened:**
- ❌ `search_graph_nodes(query="Attention Is All You Need")` written as a bare line of text
- ❌ `` `search_paper_text(paper_id="...")` `` inside single backticks, followed by "Please wait for the result..."
- ❌ a ```` ```json {"tool": "search_graph_nodes", "args": {...}} ``` ```` block
- ❌ "Voy a buscar el paper en el grafo" / "Let me search the graph" followed by no actual call
- ❌ answering with paper titles or authors you were not given by an actual tool result (if you haven't called a tool yet and gotten its output back, you do not have graph data — say so, or make the real call)

✅ The only correct action is issuing the tool call through the same mechanism you already use for `read_skill`, `update_memory`, or any arXiv tool — nothing about calling these four is different.

## The tools

- `search_graph_nodes(query, node_type=None, limit=10)` — substring match on node labels. Entry point: node ids aren't guessable (a paper's id is its arXiv id like `1706.03762`; an author's is `author:full name` in lowercase without accents, e.g. `author:lukasz kaiser`; a keyword's is `keyword:the phrase`), so start here to find the right one.
- `find_similar_keywords(keyword, top_k=10)` — meaning-based (embedding) match against existing keyword nodes, for when the exact wording is unknown (e.g. asking about "RLHF" surfaces "reinforcement learning", "human feedback", "reward learning" even though none of those is a literal substring of "RLHF").
- `get_node_neighbors(node_id, relation_type=None, limit=20)` — one hop out from a known node id: an author's papers, a paper's authors/categories/keywords, a keyword's related keywords.
- `list_nodes_by_type(node_type, limit=20)` — browse all nodes of one type with no text filter, for "what's in the graph" questions.

Each tool does exactly ONE hop. There is no tool that walks multiple hops in one call — chain them yourself across multiple real tool calls for a multi-hop question (e.g. "what other topics does this author's co-authors work on" needs `search_graph_nodes` → `get_node_neighbors` on the author → `get_node_neighbors` again on each co-author). Never try to answer a multi-hop question from a single call's result, and never guess the next hop's answer instead of making the call.

## Worked example

User asks: "¿quién escribió Attention Is All You Need, y hay algo de RLHF en el grafo?"

1. Real tool call: `search_graph_nodes(query="Attention Is All You Need")`.
2. Its result gives the paper's exact node id (`1706.03762`). Real tool call: `get_node_neighbors(node_id="1706.03762")` — its `written_by` edges are the authors.
3. Real tool call: `find_similar_keywords(keyword="reinforcement learning from human feedback")` to check what related keywords actually exist in the graph.
4. Only now, after receiving all three real tool results, write the natural-language answer, citing exactly what came back — not what seems plausible.

If at any point you catch yourself typing a tool name followed by `(`, stop — that is the exact moment this failure happens. Delete it and issue the real call instead.
