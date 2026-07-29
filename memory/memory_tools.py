import re
from datetime import datetime
from pathlib import Path

from langchain.tools import tool

# Data kept separate from code: memory/memory_tools.py is the module, the
# files generated at runtime (long_term.md, and later the memory RAG
# index) live in memory/store/.
MEMORY_DIR = (Path(__file__).parent / "store").resolve()
MEMORY_FILE = MEMORY_DIR / "long_term.md"

# Each memory entry is delimited by HTML markers with a stable 6-digit id.
# MemoryMiddleware (deepagents) already strips HTML comments before
# injecting the file into the system prompt, so these markers don't cost
# the model any tokens — but they stay in the file on disk, so our tools
# can locate and edit an exact entry without relying on heuristics over
# free-form text. This same format (delimited blocks, with timestamp and
# category) is exactly what's needed later to chunk the file for a RAG
# pipeline.
MEMORY_CATEGORIES = {"preference", "research_topic", "keyword", "paper", "note"}

ENTRY_MARKER_TOKEN = "<!-- entry:"

_ENTRY_START_RE = re.compile(r"<!-- entry:(\d{6}):start -->\n")

def _entry_end_re(entry_id: str) -> "re.Pattern[str]":
    return re.compile(rf"<!-- entry:{entry_id}:end -->\n?")

def _entry_header_re(entry_id: str) -> "re.Pattern[str]":
    return re.compile(rf"## \[{entry_id}\] (?P<category>[a-z_]+) — (?P<timestamp>[^\n]*)\n")

def _list_memory_entries(text: str) -> list[dict]:
    """Parses the entries in memory/store/long_term.md from their markers."""

    entries = []

    for start_match in _ENTRY_START_RE.finditer(text):

        entry_id = start_match.group(1)

        end_match = _entry_end_re(entry_id).search(text, start_match.end())

        if not end_match:
            continue

        header_match = _entry_header_re(entry_id).match(text, start_match.end())

        if not header_match:
            continue

        content = text[header_match.end():end_match.start()]

        entries.append({
            "id": entry_id,
            "category": header_match.group("category"),
            "timestamp": header_match.group("timestamp"),
            "content": content.strip("\n"),
            "span": (start_match.start(), end_match.end())
        })

    return entries

def _next_entry_id(text: str) -> str:
    ids = [int(m.group(1)) for m in _ENTRY_START_RE.finditer(text)]
    return f"{(max(ids) + 1) if ids else 1:06d}"

def _format_memory_entry(entry_id: str, category: str, timestamp: str, content: str) -> str:
    return (
        f"<!-- entry:{entry_id}:start -->\n"
        f"## [{entry_id}] {category} — {timestamp}\n"
        f"{content.strip()}\n"
        f"<!-- entry:{entry_id}:end -->\n"
    )

@tool
def update_memory(content: str, category: str = "note") -> str:
    """
    Adds a NEW entry to long-term memory (memory/store/long_term.md).

    category must be one of: "preference" (how you should behave),
    "research_topic" (active research topic), "keyword" (a relevant
    keyword), "paper" (a paper searched for or found), "note" (anything
    else worth remembering).

    This tool only ADDS. Every entry you save will show up in your memory
    with an id in brackets, e.g. "[000003]". If new information replaces
    or corrects something already saved, use `edit_memory` with that id
    instead of creating a duplicate or contradictory entry.
    """
    if ENTRY_MARKER_TOKEN in content:
        return "Error: content cannot include '<!-- entry:' — that's reserved internal syntax."

    if category not in MEMORY_CATEGORIES:
        return f"Error: category must be one of {sorted(MEMORY_CATEGORIES)}."

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    current = MEMORY_FILE.read_text(encoding="utf-8") if MEMORY_FILE.exists() else ""

    entry_id = _next_entry_id(current)
    timestamp = datetime.now().isoformat(timespec="seconds")

    block = _format_memory_entry(entry_id, category, timestamp, content)

    with MEMORY_FILE.open("a", encoding="utf-8") as f:
        if current and not current.endswith("\n"):
            f.write("\n")
        f.write(block)

    return f"Memory updated (entry [{entry_id}])."

@tool
def edit_memory(
    entry_id: str,
    content: str | None = None,
    category: str | None = None,
    delete: bool = False
) -> str:
    """
    Modifies or deletes an EXISTING long-term memory entry, identified by
    its id (the number in brackets you see in your memory, e.g. "000003").

    - To replace its content: pass `content` (and optionally `category`
      if that changes too).
    - To delete it entirely, because it's now obsolete or wrong:
      pass `delete=True`.

    Can only affect ONE existing entry by id — it never rewrites the rest
    of the memory. Prefer this over `update_memory` when new information
    replaces or corrects something already saved, to avoid leaving
    duplicate or contradictory entries.
    """
    if not MEMORY_FILE.exists():
        return "Error: memory is empty, there is no entry to edit."

    # Normalize the entry id because local models tend to copy literally
    # what they see in the header ("[000003]") instead of the "bare" id
    # expected as an argument — observed in real testing.
    normalized_id = entry_id.strip().strip("[]").strip()

    if normalized_id.isdigit():
        normalized_id = normalized_id.zfill(6)

    text = MEMORY_FILE.read_text(encoding="utf-8")

    entry = next(
        (e for e in _list_memory_entries(text) if e["id"] == normalized_id),
        None
    )

    if entry is None:
        return f"Error: no entry exists with id '{entry_id}'."

    entry_id = normalized_id

    start, end = entry["span"]

    if delete:
        MEMORY_FILE.write_text(text[:start] + text[end:], encoding="utf-8")
        return f"Entry [{entry_id}] deleted."

    if content is not None and ENTRY_MARKER_TOKEN in content:
        return "Error: content cannot include '<!-- entry:' — that's reserved internal syntax."

    new_category = category if category is not None else entry["category"]

    if new_category not in MEMORY_CATEGORIES:
        return f"Error: category must be one of {sorted(MEMORY_CATEGORIES)}."

    new_content = content if content is not None else entry["content"]
    timestamp = datetime.now().isoformat(timespec="seconds")

    block = _format_memory_entry(entry_id, new_category, timestamp, new_content)

    MEMORY_FILE.write_text(text[:start] + block + text[end:], encoding="utf-8")

    return f"Entry [{entry_id}] updated."
