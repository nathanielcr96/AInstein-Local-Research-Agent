import logging
from collections import OrderedDict
from pathlib import Path
from typing import Any

import aiosqlite

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.middleware.skills import SkillsMiddleware

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain_ollama import ChatOllama

from core.tools import read_skill
from core.arxiv_download import download_paper as custom_download_paper
from memory.memory_tools import MEMORY_FILE, _list_memory_entries, update_memory, edit_memory
from memory.memory_rag import make_search_memory_tool
from core.middleware import ExcludeToolsMiddleware, EnsureFinalAnswerMiddleware, PaperMemoryMiddleware, ArxivTimeoutMiddleware
from prompts.research_agent_prompt import SYSTEM_PROMPT
from prompts.skills_prompt import CUSTOM_SKILLS_SYSTEM_PROMPT
from prompts.memory_prompt import MEMORY_PROMPT_TEMPLATE, MEMORY_SEARCH_PROMPT
from prompts.arxiv_prompt import ARXIV_PROMPT

logger = logging.getLogger(__name__)

# root_dir="." resolves against the process's cwd at the moment the
# backend is created (Path(".").resolve()), not against the project
# folder. If chainlit is launched from a different directory, this would
# point to the wrong place. Anchoring it to this file's folder makes it
# independent of where the app is started from.
PROJECT_DIR = Path(__file__).parent.resolve()

backend = FilesystemBackend(root_dir=PROJECT_DIR,
                            virtual_mode = True)
tools = [read_skill, update_memory, edit_memory]

# LangGraph checkpointer: persists the full conversation state (messages,
# tool calls, results) in a local .sqlite, indexed by thread_id. Replaces
# the manual chat_history reconstruction in app.py.
#
# SqliteSaver (synchronous) explicitly rejects the async methods that
# astream_events needs ("does not support async methods"), so
# AsyncSqliteSaver + aiosqlite is required. The aiosqlite connection is an
# async resource, so it's created lazily the first time it's requested
# (it can't be opened at module import time, which is synchronous code)
# and reused afterwards.
CHECKPOINT_DB_PATH = PROJECT_DIR / "checkpoints.sqlite"

_checkpointer: AsyncSqliteSaver | None = None

async def get_checkpointer() -> AsyncSqliteSaver:

    global _checkpointer

    if _checkpointer is None:

        conn = await aiosqlite.connect(str(CHECKPOINT_DB_PATH))

        _checkpointer = AsyncSqliteSaver(conn)

        await _checkpointer.setup()

    return _checkpointer

# arXiv MCP server (blazickjp/arxiv-mcp-server), not a pip dependency —
# launched on demand via `uv tool run --from "arxiv-mcp-server[pdf]" ...`,
# which lets uv resolve/build its isolated environment itself, with no
# separate manual install step required. The `[pdf]` extra is pinned
# explicitly in the run command (not left to a one-off `uv tool install`
# elsewhere) because `read_paper` needs it for PDF-to-text conversion of
# any paper it re-reads that was downloaded via the PDF fallback path —
# without it, that fails with "PDF conversion requires the pdf extra",
# verified to happen even when the extra was previously installed
# separately, since `uv tool run` doesn't reliably reuse that install.
# Runs as a local subprocess over stdio — no API keys, the arXiv API is
# public. We only actually use search_papers, get_abstract, read_paper,
# list_papers, citation_graph, watch_topic/check_alerts from it —
# download_paper is replaced with our own in-process implementation, and
# semantic_search/reindex are dropped entirely (see below). Downloaded
# papers are saved to papers/, inside the project — the local paper
# repository.
#
# get_tools() is cached the same way as the checkpointer: it's an async
# resource that can't be resolved at module import time, and there's no
# point relaunching the MCP subprocess on every message.
#
# Only SUCCESS is cached. If it fails (server not installed yet, network
# hiccup, etc.), _arxiv_tools stays None and the next build_agent() tries
# again — previously the failure was also cached ([]), so a one-off
# problem left arXiv tools disabled until the whole app restarted, even
# after the real problem had already been resolved.
PAPERS_STORAGE_PATH = PROJECT_DIR / "papers"

_arxiv_tools: list | None = None

async def get_arxiv_tools() -> list:

    global _arxiv_tools

    if _arxiv_tools is not None:
        return _arxiv_tools

    try:

        mcp_client = MultiServerMCPClient({
            "arxiv": {
                "command": "uv",
                "args": [
                    "tool", "run",
                    "--from", "arxiv-mcp-server[pdf]", "arxiv-mcp-server",
                    "--storage-path", str(PAPERS_STORAGE_PATH)
                ],
                "transport": "stdio"
            }
        })

        _arxiv_tools = await mcp_client.get_tools()

    except Exception:

        logger.exception(
            "Could not connect to the arXiv MCP server "
            "(is it installed? `uv tool install arxiv-mcp-server`). "
            "The agent keeps working without arXiv tools; "
            "it will retry the next time the agent is built."
        )

        return []

    return _arxiv_tools

# create_deep_agent always adds filesystem tools (ls, read_file, write_file,
# edit_file, glob, grep) even without passing a backend intended for that.
# We hide them from the model until we explicitly decide which ones we need.
#
# "task" is also hidden: it launches subagents with their own internal
# FilesystemMiddleware, which does NOT respect this same filter (they have
# full access to read_file/write_file/etc. even though the main agent can't
# see them). Until we redesign the subagents explicitly, hiding it avoids
# that bypass.
HIDDEN_TOOLS = {"ls", "read_file", "write_file", "edit_file", "glob", "grep", "execute", "task"}

SKILLS_SOURCES = ["./skills/"]

# Long-term memory is no longer injected whole into the system prompt
# (that's what motivated asking for RAG: the .md only grows —
# update_memory never deletes — and loading it whole every turn would
# compete more and more for num_ctx). Instead the prompt only carries a
# lightweight index (id, category, timestamp, no content) and the model
# retrieves the actual content on demand with `search_memory`, in the same
# spirit as `read_skill` with skills.
def _build_memory_index_section() -> str:

    if not MEMORY_FILE.exists():
        return "You have 0 long-term memory entries yet."

    entries = _list_memory_entries(MEMORY_FILE.read_text(encoding="utf-8"))

    if not entries:
        return "You have 0 long-term memory entries yet."

    lines = [f"- [{e['id']}] {e['category']} — {e['timestamp']}" for e in entries]

    return f"You have {len(entries)} long-term memory entries:\n" + "\n".join(lines)

# Rebuilding the entire agent (reloading skills, rebinding tools,
# assembling the whole middleware stack) on every message is expensive and
# mostly unnecessary: it's almost always the same settings as the
# previous turn. It's cached by the combination of settings that actually
# change its behavior — but the memory index (_build_memory_index_section)
# gets "baked" into the system prompt at the moment the agent is built,
# so the mtime of long_term.md has to be part of the key: otherwise, after
# an update_memory/edit_memory the cached agent would keep showing the
# old index until some other setting changed. Bounded with a max size
# (LRU) so it doesn't grow without limit in a long session with many
# memory edits.
_AGENT_CACHE_MAX_SIZE = 8

_agent_cache: "OrderedDict[tuple, Any]" = OrderedDict()

async def build_agent(
    model_name: str,
    temperature: float = 0,
    num_ctx: int = 16384,
    embedding_provider: str | None = None,
    embedding_model: str | None = None
):

    memory_mtime = MEMORY_FILE.stat().st_mtime if MEMORY_FILE.exists() else None

    # Resolved BEFORE checking the cache: get_arxiv_tools() already has
    # its own cache (cheap after the first success), and we need to know
    # whether arXiv tools are available RIGHT NOW so the cache key
    # reflects it. Without this, an agent cached while arXiv was failing
    # would keep being served (without those tools, with a prompt that no
    # longer mentions them) even after arXiv recovered.
    arxiv_tools = await get_arxiv_tools()

    # download_paper is replaced with our own in-process implementation
    # (core/arxiv_download.py) — the MCP-provided one goes through the
    # arxiv-mcp-server subprocess over stdio, which was verified to
    # sometimes take minutes or hang indefinitely for this specific tool
    # on this setup, even when the same underlying fetch/convert logic
    # completes in under a minute run directly. The other arXiv tools
    # (search_papers, read_paper, list_papers, ...) are left untouched —
    # they write/read the same papers/ folder either way, so nothing else
    # needs to change for them to see files this tool saves.
    #
    # semantic_search/reindex are dropped entirely rather than replaced:
    # they only embed each paper's short abstract (never the full text we
    # actually save), don't support author/category/date filtering, and
    # duplicate what our own search_memory (FAISS + reranker, over the
    # same paper abstracts via PaperMemoryMiddleware) already covers —
    # not worth the sentence-transformers model + SQLite index they'd
    # otherwise load into memory for a feature we don't use.
    if arxiv_tools:
        excluded = {"download_paper", "semantic_search", "reindex"}
        arxiv_tools = [t for t in arxiv_tools if t.name not in excluded] + [custom_download_paper]

    has_search_memory = bool(embedding_provider and embedding_model)

    cache_key = (
        model_name, temperature, num_ctx,
        embedding_provider, embedding_model, memory_mtime,
        bool(arxiv_tools)
    )

    if cache_key in _agent_cache:
        _agent_cache.move_to_end(cache_key)
        return _agent_cache[cache_key]

    # create_deep_agent unconditionally adds its own automatic
    # SummarizationMiddleware (it can't be removed or replaced by ours —
    # two middleware with the same name make agent creation fail with
    # "Please remove duplicate middleware instances"). That automatic one
    # computes its threshold from llm.profile["max_input_tokens"]; ChatOllama
    # doesn't fill that profile in on its own (always None), so without
    # this it would fall back to a fixed 170,000 tokens, way above the
    # real num_ctx of any local model — in practice it would never
    # trigger and the context would end up overflowing num_ctx. By
    # passing the real num_ctx as the profile, the automatic one uses its
    # fraction-based thresholds (85% triggers summarization, the last 10%
    # is kept) already correctly computed against this model's real
    # context.
    llm = ChatOllama(
        model=model_name,
        temperature=temperature,
        num_ctx = num_ctx,
        profile = {"max_input_tokens": num_ctx}
    )

    # search_memory is built per session, bound to the embedding model
    # chosen in the chat settings (it isn't fixed for the whole app,
    # unlike read_skill/update_memory/edit_memory). If no embedding
    # model is available, it's omitted: memory can still be written/edited,
    # it just can't be searched semantically.
    agent_tools = list(tools)

    if has_search_memory:
        agent_tools.append(make_search_memory_tool(embedding_provider, embedding_model))

    agent_tools += arxiv_tools

    # The prompt only promises what agent_tools actually contains —
    # previously ARXIV_PROMPT and the mention of search_memory were always
    # concatenated, even when those tools hadn't actually ended up in
    # agent_tools (embeddings not configured, or arXiv down), and the
    # model could try to call tools that didn't really exist.
    memory_section = MEMORY_PROMPT_TEMPLATE.format(
        memory_index=_build_memory_index_section()
    )

    if has_search_memory:
        memory_section = f"{memory_section}\n\n{MEMORY_SEARCH_PROMPT}"

    prompt_parts = [SYSTEM_PROMPT, memory_section]

    if arxiv_tools:
        prompt_parts.append(ARXIV_PROMPT)

    full_system_prompt = "\n\n".join(prompt_parts)

    checkpointer = await get_checkpointer()

    agent = create_deep_agent(
        llm,
        agent_tools,
        system_prompt = full_system_prompt,
        backend = backend,
        checkpointer = checkpointer,
        middleware = [
            SkillsMiddleware(
                backend=backend,
                sources=SKILLS_SOURCES,
                system_prompt=CUSTOM_SKILLS_SYSTEM_PROMPT
            ),
            ExcludeToolsMiddleware(excluded=HIDDEN_TOOLS),
            EnsureFinalAnswerMiddleware(max_retries=2),
            PaperMemoryMiddleware(),
            ArxivTimeoutMiddleware()
        ],
        # debug=True makes LangGraph print every internal state update via a
        # plain print(), which on Windows encodes to the console's cp1252
        # codepage — verified to crash the whole turn with
        # UnicodeEncodeError the moment any tool result contains a
        # non-ASCII character (e.g. the Greek "α" in "α-MoO3", common in
        # physics papers). Keep this False outside of active debugging.
        debug = False
    )

    _agent_cache[cache_key] = agent
    _agent_cache.move_to_end(cache_key)

    if len(_agent_cache) > _AGENT_CACHE_MAX_SIZE:
        _agent_cache.popitem(last=False)

    return agent