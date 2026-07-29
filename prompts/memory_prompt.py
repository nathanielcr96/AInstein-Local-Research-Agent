# Long-term memory prompt. {memory_index} is filled in by
# graph.py:_build_memory_index_section() with the lightweight index (id,
# category, timestamp) read from memory/store/long_term.md — never the
# full content, see memory/memory_rag.py for why.
#
# Deliberately doesn't mention search_memory here: that tool only exists
# if an embedding model is configured (see graph.py:build_agent). If not,
# MEMORY_SEARCH_PROMPT isn't appended, so the prompt never promises the
# model a tool it doesn't actually have.
MEMORY_PROMPT_TEMPLATE = """## Long-term memory

{memory_index}

This is only a lightweight index (id, category, timestamp) — it does NOT
include the content.

To persist new knowledge:
- `update_memory(content=..., category=...)` adds a NEW entry. category is
  one of: preference, research_topic, keyword, paper, note.
- `edit_memory(entry_id=..., content=..., category=...)` REPLACES or
  CORRECTS an existing entry — use this instead of creating a duplicate
  when something changes.
- `edit_memory(entry_id=..., delete=True)` removes an entry that is now
  obsolete or wrong.

You do not have a generic file-writing tool: `update_memory` and
`edit_memory` are the only way to persist long-term memory, and they only
ever touch your own memory file."""

# Appended to MEMORY_PROMPT_TEMPLATE only when search_memory is actually
# available (embedding_provider + embedding_model configured).
MEMORY_SEARCH_PROMPT = """To read the full content of an entry (not just its index line above), \
call `search_memory(query, k=5)` — semantic search over long-term memory. \
Do this proactively when the topic could relate to something you've saved \
before: active research, user preferences, prior papers."""
