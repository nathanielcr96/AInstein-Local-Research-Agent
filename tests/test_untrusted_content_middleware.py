"""Unit tests for UntrustedContentMiddleware (core/middleware.py), step 1.1 of
SECURITY_IMPLEMENTATION_PLAN.md. No Ollama needed — these construct a ToolCallRequest
directly and call wrap_tool_call/awrap_tool_call in isolation, the same way the middleware
itself is exercised inside the real agent's ToolNode.

Run with: python tests/test_untrusted_content_middleware.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain.agents.middleware.types import ToolCallRequest
from langchain_core.messages import ToolMessage

import core.middleware as mw
from core.arxiv_download import _CONTENT_WARNING, _CONTENT_WARNING_FOOTER
from memory.graph_tools import _GRAPH_LABEL_WARNING, _GRAPH_LABEL_WARNING_FOOTER

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        _FAILURES.append(label)


def make_request(name: str, call_id: str = "call-1") -> ToolCallRequest:
    return ToolCallRequest(
        tool_call={"name": name, "args": {}, "id": call_id},
        tool=None,
        state={},
        runtime=None,
    )


def handler_returning(text: str, *, name: str = "some_tool", call_id: str = "call-1"):
    def _handler(request):
        return ToolMessage(content=text, tool_call_id=call_id, name=name)
    return _handler


def async_handler_returning(text: str, *, name: str = "some_tool", call_id: str = "call-1"):
    async def _handler(request):
        return ToolMessage(content=text, tool_call_id=call_id, name=name)
    return _handler


def test_default_set_contains_the_eight_content_tools():
    """Step 1.3: the six arXiv content tools from step 1.2 plus
    search_paper_content (memory/paper_rag.py), plus analyze_paper_figures
    (core/figure_analysis.py, step 4.4) are wrapped with the long framing.
    watch_topic/check_alerts are deliberately NOT included yet (see the comment above
    _UNTRUSTED_CONTENT_TOOLS). The four graph tools live in the separate
    _UNTRUSTED_LABEL_TOOLS set (step 1.4), not here."""
    expected = {
        "download_paper", "search_papers", "get_abstract",
        "read_paper", "list_papers", "citation_graph",
        "search_paper_content", "analyze_paper_figures",
    }
    check("default set == the eight content tools", mw._UNTRUSTED_CONTENT_TOOLS == frozenset(expected))
    check("watch_topic not included (yet)", "watch_topic" not in mw._UNTRUSTED_CONTENT_TOOLS)
    check("check_alerts not included (yet)", "check_alerts" not in mw._UNTRUSTED_CONTENT_TOOLS)
    check("search_graph_nodes not in the long-warning set", "search_graph_nodes" not in mw._UNTRUSTED_CONTENT_TOOLS)


def test_analyze_paper_figures_wrapped_by_default():
    """Structural verification only — no vision-capable model is installed in this
    environment, so this can't be checked live end-to-end the way download_paper/
    get_abstract were (step 1.2). Uses a synthetic result matching the tool's real
    JSON shape (core/figure_analysis.py: status/paper_id/figures[])."""
    middleware = mw.UntrustedContentMiddleware()
    raw_json = (
        '{"status": "success", "paper_id": "1234.5678", "figures": '
        '[{"page": 3, "index": 0, "description": "Figure 1 appears to show a diagram."}]}'
    )
    request = make_request("analyze_paper_figures")
    result = middleware.wrap_tool_call(request, handler_returning(raw_json))
    check("analyze_paper_figures: wrapped by default", result.content.startswith(_CONTENT_WARNING))
    check("analyze_paper_figures: footer present", result.content.endswith(_CONTENT_WARNING_FOOTER))
    check("analyze_paper_figures: original JSON preserved inside", raw_json in result.content)


def test_default_label_set_contains_the_four_graph_tools():
    """Step 1.4: the four graph tools (memory/graph_tools.py) are wrapped with the
    short, one-line label framing, kept separate from the long-content set."""
    expected = {
        "search_graph_nodes", "get_node_neighbors",
        "list_nodes_by_type", "find_similar_keywords",
    }
    check("default label set == the four graph tools", mw._UNTRUSTED_LABEL_TOOLS == frozenset(expected))
    check("no overlap between the two sets", mw._UNTRUSTED_CONTENT_TOOLS.isdisjoint(mw._UNTRUSTED_LABEL_TOOLS))


def test_graph_tool_wrapped_with_short_label_warning():
    """A graph tool's plain-text result gets the SHORT warning, not the long
    paragraph-length one meant for paper prose."""
    middleware = mw.UntrustedContentMiddleware()
    labels = "Attention Is All You Need (type=paper, id=1706.03762)\nAaren (type=keyword, id=keyword:aaren)"
    request = make_request("search_graph_nodes")
    result = middleware.wrap_tool_call(request, handler_returning(labels))
    check("graph tool: wrapped with the SHORT header", result.content.startswith(_GRAPH_LABEL_WARNING))
    check("graph tool: NOT wrapped with the long header", not result.content.startswith(_CONTENT_WARNING))
    check("graph tool: short footer present", result.content.endswith(_GRAPH_LABEL_WARNING_FOOTER))
    check("graph tool: labels preserved", labels in result.content)


def test_graph_tool_never_double_wrapped():
    middleware = mw.UntrustedContentMiddleware()
    already_wrapped = _GRAPH_LABEL_WARNING + "some label" + _GRAPH_LABEL_WARNING_FOOTER
    request = make_request("get_node_neighbors")
    result = middleware.wrap_tool_call(request, handler_returning(already_wrapped))
    check("graph tool: no double wrap", result.content == already_wrapped)
    check(
        "graph tool: short header appears exactly once",
        result.content.count(_GRAPH_LABEL_WARNING.strip()) == 1,
    )


def test_search_paper_content_wrapped_by_default():
    """search_paper_content returns plain text (never JSON) — confirm the whole
    multi-passage block gets wrapped once, header at the very start, footer at the
    very end, same as any other tool in the set."""
    middleware = mw.UntrustedContentMiddleware()
    passages = (
        "Title: Attention Is All You Need\nAuthors: Vaswani et al.\narXiv id: 1706.03762\n\n"
        "We propose the Transformer...\n\n---\n\n"
        "Title: Attention Is All You Need\nAuthors: Vaswani et al.\narXiv id: 1706.03762\n\n"
        "The encoder is composed of a stack of N=6 identical layers..."
    )
    request = make_request("search_paper_content")
    result = middleware.wrap_tool_call(request, handler_returning(passages))
    check("search_paper_content: wrapped by default", result.content.startswith(_CONTENT_WARNING))
    check("search_paper_content: footer present", result.content.endswith(_CONTENT_WARNING_FOOTER))
    check("search_paper_content: both passages preserved", passages in result.content)
    check("search_paper_content: header appears once, not per-passage", result.content.count(_CONTENT_WARNING.strip()) == 1)


def test_download_paper_wrapped_by_default():
    """With the real (non-empty) default set, download_paper's raw JSON — no longer
    wrapped by _success_payload itself (core/arxiv_download.py, step 1.2) — must come
    back wrapped by the middleware instead."""
    middleware = mw.UntrustedContentMiddleware()
    raw_json = '{"status": "success", "message": "ok", "paper_id": "1234.5678", "content": "the paper text"}'
    request = make_request("download_paper")
    result = middleware.wrap_tool_call(request, handler_returning(raw_json))
    check("download_paper: wrapped by default", result.content.startswith(_CONTENT_WARNING))
    check("download_paper: footer present", result.content.endswith(_CONTENT_WARNING_FOOTER))
    check("download_paper: original JSON preserved inside", raw_json in result.content)


def test_unrelated_tool_still_unaffected():
    """A tool with no security relevance (not in the set) is still left alone."""
    middleware = mw.UntrustedContentMiddleware()
    original = "unrelated tool output"
    request = make_request("update_memory")
    result = middleware.wrap_tool_call(request, handler_returning(original))
    check("unrelated tool: unchanged", result.content == original)
    check("unrelated tool: no warning added", _CONTENT_WARNING not in result.content)


def test_wraps_tool_in_the_set():
    """With a tool name temporarily added to the set (simulating step 1.2), its
    result should come back with the header before and the footer after."""
    original_set = mw._UNTRUSTED_CONTENT_TOOLS
    mw._UNTRUSTED_CONTENT_TOOLS = frozenset({"some_tool"})
    try:
        middleware = mw.UntrustedContentMiddleware()
        request = make_request("some_tool")
        result = middleware.wrap_tool_call(request, handler_returning("raw paper text"))
        check(
            "wrapped result starts with the header",
            result.content.startswith(_CONTENT_WARNING),
        )
        check(
            "wrapped result ends with the footer",
            result.content.endswith(_CONTENT_WARNING_FOOTER),
        )
        check(
            "original text preserved in the middle",
            "raw paper text" in result.content,
        )
        check("tool_call_id preserved", result.tool_call_id == "call-1")
        check("name preserved", result.name == "some_tool")
    finally:
        mw._UNTRUSTED_CONTENT_TOOLS = original_set


def test_does_not_wrap_tool_not_in_the_set():
    original_set = mw._UNTRUSTED_CONTENT_TOOLS
    mw._UNTRUSTED_CONTENT_TOOLS = frozenset({"some_tool"})
    try:
        middleware = mw.UntrustedContentMiddleware()
        request = make_request("other_tool")
        result = middleware.wrap_tool_call(request, handler_returning("raw text"))
        check("tool not in set: unchanged", result.content == "raw text")
    finally:
        mw._UNTRUSTED_CONTENT_TOOLS = original_set


def test_never_double_wraps():
    """If a tool's own handler already returned text wrapped with the header
    (e.g. download_paper's _success_payload, until step 1.2 removes that manual
    wrapping), the middleware must not wrap it a second time."""
    original_set = mw._UNTRUSTED_CONTENT_TOOLS
    mw._UNTRUSTED_CONTENT_TOOLS = frozenset({"download_paper"})
    try:
        middleware = mw.UntrustedContentMiddleware()
        already_wrapped = _CONTENT_WARNING + "paper text" + _CONTENT_WARNING_FOOTER
        request = make_request("download_paper")
        result = middleware.wrap_tool_call(request, handler_returning(already_wrapped))
        check(
            "no double wrap: header appears exactly once",
            result.content.count(_CONTENT_WARNING.strip()) == 1,
        )
        check("no double wrap: content unchanged", result.content == already_wrapped)
    finally:
        mw._UNTRUSTED_CONTENT_TOOLS = original_set


def test_async_path_matches_sync():
    original_set = mw._UNTRUSTED_CONTENT_TOOLS
    mw._UNTRUSTED_CONTENT_TOOLS = frozenset({"some_tool"})
    try:
        middleware = mw.UntrustedContentMiddleware()
        request = make_request("some_tool")
        result = asyncio.run(
            middleware.awrap_tool_call(request, async_handler_returning("raw paper text"))
        )
        check(
            "async: wrapped result starts with the header",
            result.content.startswith(_CONTENT_WARNING),
        )
        check(
            "async: wrapped result ends with the footer",
            result.content.endswith(_CONTENT_WARNING_FOOTER),
        )
    finally:
        mw._UNTRUSTED_CONTENT_TOOLS = original_set


def test_non_tool_message_passes_through():
    """A result that isn't a ToolMessage (e.g. a Command) must be returned as-is,
    never crash _maybe_wrap."""
    original_set = mw._UNTRUSTED_CONTENT_TOOLS
    mw._UNTRUSTED_CONTENT_TOOLS = frozenset({"some_tool"})
    try:
        middleware = mw.UntrustedContentMiddleware()
        sentinel = {"not": "a ToolMessage"}
        request = make_request("some_tool")
        result = middleware.wrap_tool_call(request, lambda req: sentinel)
        check("non-ToolMessage result passed through unchanged", result is sentinel)
    finally:
        mw._UNTRUSTED_CONTENT_TOOLS = original_set


if __name__ == "__main__":
    test_default_set_contains_the_eight_content_tools()
    test_default_label_set_contains_the_four_graph_tools()
    test_download_paper_wrapped_by_default()
    test_analyze_paper_figures_wrapped_by_default()
    test_search_paper_content_wrapped_by_default()
    test_graph_tool_wrapped_with_short_label_warning()
    test_graph_tool_never_double_wrapped()
    test_unrelated_tool_still_unaffected()
    test_wraps_tool_in_the_set()
    test_does_not_wrap_tool_not_in_the_set()
    test_never_double_wraps()
    test_async_path_matches_sync()
    test_non_tool_message_passes_through()

    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} check(s) FAILED:")
        for f in _FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checks passed.")
