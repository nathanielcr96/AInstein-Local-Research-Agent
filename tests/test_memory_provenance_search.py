"""Unit tests for step 2.2 of SECURITY_IMPLEMENTATION_PLAN.md — search_memory (memory/
memory_rag.py) must prepend a short untrusted-content warning to a retrieved entry whose
content has `Source: external...` (tagged by step 2.1's PaperMemoryMiddleware), and leave
any other entry (preferences, research topics, the agent's own notes) exactly as-is.

No Ollama, no real index/file: exercises _is_external_source and the entry-formatting
logic directly against synthetic entry content.

Run with: python tests/test_memory_provenance_search.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory.memory_rag import (
    _is_external_source,
    _MEMORY_EXTERNAL_SOURCE_WARNING,
    _MEMORY_EXTERNAL_SOURCE_WARNING_FOOTER,
)

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        _FAILURES.append(label)


PAPER_ENTRY = (
    "arXiv ID: 9999.00001\n"
    "Source: external (arXiv), unverified\n"
    "Title: A Paper\n"
    "Abstract: some abstract text\n"
)

OLD_PAPER_ENTRY_NO_SOURCE_YET = (
    "arXiv ID: 1706.03762\n"
    "Title: Attention Is All You Need\n"
    "Abstract: We propose a new architecture...\n"
)

PREFERENCE_ENTRY = "User prefers concise answers with no filler.\n"

RESEARCH_TOPIC_ENTRY = "Active research topic: reinforcement learning from human feedback.\n"


def test_paper_entry_with_source_is_detected():
    check("tagged paper entry -> external", _is_external_source(PAPER_ENTRY) is True)


def test_old_paper_entry_without_source_is_not_detected():
    """An entry saved before step 2.1 existed has no Source field — must NOT be
    treated as external just because it happens to have an arXiv ID."""
    check("untagged old paper entry -> not external", _is_external_source(OLD_PAPER_ENTRY_NO_SOURCE_YET) is False)


def test_preference_entry_is_not_detected():
    check("preference entry -> not external", _is_external_source(PREFERENCE_ENTRY) is False)


def test_research_topic_entry_is_not_detected():
    check("research_topic entry -> not external", _is_external_source(RESEARCH_TOPIC_ENTRY) is False)


def _format_entry_like_search_memory(entry_id: str, category: str, timestamp: str, content: str) -> str:
    # Mirrors search_memory's own _format_entry closure (memory/memory_rag.py) without
    # needing a real FAISS/Document round trip.
    block = f"[{entry_id}] {category} — {timestamp}\n{content}"
    if _is_external_source(content):
        return _MEMORY_EXTERNAL_SOURCE_WARNING + block + _MEMORY_EXTERNAL_SOURCE_WARNING_FOOTER
    return block


def test_mixed_results_only_external_entry_gets_wrapped():
    """The exact scenario the plan's verification calls for: search results containing
    both a tagged paper entry and a non-paper entry (a preference) in the same call —
    only the paper entry should carry the warning."""
    paper_block = _format_entry_like_search_memory("000172", "paper", "2026-09-28T09:53:25", PAPER_ENTRY)
    pref_block = _format_entry_like_search_memory("000005", "preference", "2026-01-01T00:00:00", PREFERENCE_ENTRY)

    check("paper entry starts with the warning", paper_block.startswith(_MEMORY_EXTERNAL_SOURCE_WARNING))
    check("paper entry ends with the footer", paper_block.endswith(_MEMORY_EXTERNAL_SOURCE_WARNING_FOOTER))
    check("paper entry id/category/timestamp preserved", "[000172] paper — 2026-09-28T09:53:25" in paper_block)

    check("preference entry has NO warning", not pref_block.startswith(_MEMORY_EXTERNAL_SOURCE_WARNING))
    check("preference entry unchanged otherwise", pref_block == f"[000005] preference — 2026-01-01T00:00:00\n{PREFERENCE_ENTRY}")


if __name__ == "__main__":
    test_paper_entry_with_source_is_detected()
    test_old_paper_entry_without_source_is_not_detected()
    test_preference_entry_is_not_detected()
    test_research_topic_entry_is_not_detected()
    test_mixed_results_only_external_entry_gets_wrapped()

    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} check(s) FAILED:")
        for f in _FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checks passed.")
