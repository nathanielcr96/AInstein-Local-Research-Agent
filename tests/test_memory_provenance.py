"""Unit tests for step 2.1 of SECURITY_IMPLEMENTATION_PLAN.md — provenance tagging on
memory entries PaperMemoryMiddleware auto-saves (core/middleware.py). No Ollama needed,
and no real file I/O: update_memory/edit_memory/_find_paper_entry are monkeypatched on the
core.middleware module so this never touches memory/store/long_term.md.

The real end-to-end behavior (a genuinely new paper saved via a live agent turn, checked by
hand against long_term.md, confirming an older pre-existing entry is left untouched) was
verified separately and is documented in the chat history for this step, not re-run here —
this file protects the deterministic pieces against regression.

Run with: python tests/test_memory_provenance.py
"""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.messages import ToolMessage

import core.middleware as mw
from memory.memory_tools import _format_kv_block, _parse_kv_block, _PAPER_FIELD_ORDER

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        _FAILURES.append(label)


def test_source_is_in_the_field_order_right_after_arxiv_id():
    check(
        "Source comes right after arXiv ID in _PAPER_FIELD_ORDER",
        _PAPER_FIELD_ORDER.index("Source") == _PAPER_FIELD_ORDER.index("arXiv ID") + 1,
    )


def test_format_kv_block_places_source_second():
    block = _format_kv_block({
        "arXiv ID": "1234.5678",
        "Source": "external (arXiv), unverified",
        "Title": "A Paper",
        "Abstract": "some abstract text",
    })
    lines = block.splitlines()
    check("line 0 is arXiv ID", lines[0] == "arXiv ID: 1234.5678")
    check("line 1 is Source", lines[1] == "Source: external (arXiv), unverified")
    check("Title still present further down", "Title: A Paper" in lines)


def test_format_kv_block_omits_source_when_absent():
    """An old entry with no Source key (pre-step-2.1) must not have one invented."""
    block = _format_kv_block({"arXiv ID": "1234.5678", "Title": "A Paper"})
    check("no Source line when the field was never set", "Source:" not in block)


class _FakeResult(SimpleNamespace):
    """Minimal ToolMessage-shaped stand-in — avoids needing a real ToolMessage here
    since _record_paper only reads .content via _tool_message_text."""


def _make_tool_message(payload: dict) -> ToolMessage:
    return ToolMessage(content=json.dumps(payload), tool_call_id="x", name="get_abstract")


def test_new_entry_gets_tagged_get_abstract():
    """A brand-new paper (no existing memory entry) saved via get_abstract gets
    Source set, without touching real files — update_memory/_find_paper_entry
    are monkeypatched to capture what would have been written."""
    original_update_memory = mw.update_memory
    original_find_entry = mw._find_paper_entry
    captured = {}

    def fake_update_memory_func(*, content, category):
        captured["content"] = content
        captured["category"] = category

    mw.update_memory = SimpleNamespace(func=fake_update_memory_func)
    mw._find_paper_entry = lambda paper_id: None  # no existing entry -> "new" branch

    try:
        middleware = mw.PaperMemoryMiddleware()
        payload = {
            "status": "success", "paper_id": "9999.00001",
            "title": "A Brand New Paper", "authors": ["Jane Doe"],
            "categories": ["cs.AI"], "published": "2026-01-01T00:00:00Z",
            "abstract": "an abstract",
        }
        middleware._record_paper("get_abstract", {"paper_id": "9999.00001"}, _make_tool_message(payload))

        fields = _parse_kv_block(captured.get("content", ""))
        check("new-entry write happened", "content" in captured)
        check("category is paper", captured.get("category") == "paper")
        check("Source field present", fields.get("Source") == "external (arXiv), unverified")
        check("Title still correct", fields.get("Title") == "A Brand New Paper")
    finally:
        mw.update_memory = original_update_memory
        mw._find_paper_entry = original_find_entry


def test_merge_into_existing_entry_adds_source_too():
    """An OLDER entry that predates this change (no Source field yet) gets Source
    added if it's touched again — the organic back-fill path described in the
    code comment, not a separate migration script."""
    original_edit_memory = mw.edit_memory
    original_find_entry = mw._find_paper_entry
    captured = {}

    existing_content = "arXiv ID: 8888.00002\nTitle: An Old Paper\n"

    def fake_edit_memory_func(*, entry_id, content, category):
        captured["entry_id"] = entry_id
        captured["content"] = content
        captured["category"] = category

    mw.edit_memory = SimpleNamespace(func=fake_edit_memory_func)
    mw._find_paper_entry = lambda paper_id: {"id": "000042", "content": existing_content}

    try:
        middleware = mw.PaperMemoryMiddleware()
        payload = {"status": "success", "paper_id": "8888.00002"}
        middleware._record_paper("download_paper", {"paper_id": "8888.00002"}, _make_tool_message(payload))

        fields = _parse_kv_block(captured.get("content", ""))
        check("merge write happened", "content" in captured)
        check("existing Title preserved", fields.get("Title") == "An Old Paper")
        check("Source back-filled on the older entry", fields.get("Source") == "external (arXiv), unverified")
        check("Local file field added", "Local file" in fields)
    finally:
        mw.edit_memory = original_edit_memory
        mw._find_paper_entry = original_find_entry


if __name__ == "__main__":
    test_source_is_in_the_field_order_right_after_arxiv_id()
    test_format_kv_block_places_source_second()
    test_format_kv_block_omits_source_when_absent()
    test_new_entry_gets_tagged_get_abstract()
    test_merge_into_existing_entry_adds_source_too()

    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} check(s) FAILED:")
        for f in _FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checks passed.")
