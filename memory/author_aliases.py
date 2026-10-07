"""Author aliases: which author nodes a person has confirmed are the same researcher.

The knowledge graph identifies an author by their accent- and case-folded name and nothing else, so
"Quoc Le" and "Quoc V. Le" are two nodes (see README, "Graph construction has real limits"). The graph is
also DERIVED: `python -m memory.knowledge_graph` rebuilds it from long_term.md. So a merge done only inside
graph.sqlite would come back on the next rebuild. The decision therefore lives here, in
`memory/store/author_aliases.json`, and `memory.knowledge_graph._upsert_author` consults it whenever it
ingests an author — live or in a rebuild.

Only a person makes an entry (`python -m memory.graph_hygiene --merge ... --yes`); nothing in the agent
writes this file. To undo a merge: delete its entry here and rebuild the graph.

File format:
    {"merges": [{"canonical": "author:quoc v. le", "label": "Quoc V. Le",
                 "aliases": ["author:quoc le"], "confirmed": "2026-09-30T12:00:00", "note": "..."}]}
"""
import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

ALIASES_PATH = Path(__file__).parent / "store" / "author_aliases.json"

_cache: dict = {"key": None, "map": {}}


def _read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        merges = data["merges"]
        if not isinstance(merges, list):
            raise ValueError("'merges' is not a list")
        return merges
    except Exception:  # noqa: BLE001 - a broken file must never break ingestion, but must not pass silently
        logger.warning("Ignoring %s: it could not be read as an author-aliases file", path, exc_info=True)
        return []


def load(path: Path | None = None) -> dict[str, tuple[str, str]]:
    """{alias author id: (canonical author id, canonical label)}. Empty when the file is missing or broken.

    Cached by modification time: ingesting a paper looks up a handful of authors, a rebuild hundreds."""
    path = path or ALIASES_PATH
    try:
        stamp = (str(path), path.stat().st_mtime_ns)
    except OSError:
        return {}
    if _cache["key"] == stamp:
        return _cache["map"]
    mapping: dict[str, tuple[str, str]] = {}
    for m in _read(path):
        try:
            for alias in m["aliases"]:
                mapping[alias] = (m["canonical"], m["label"])
        except (KeyError, TypeError):
            logger.warning("Skipping a malformed entry in %s: %r", path, m)
    _cache["key"], _cache["map"] = stamp, mapping
    return mapping


def lookup(author_id: str, path: Path | None = None) -> tuple[str, str] | None:
    return load(path).get(author_id)


def add_merge(canonical_id: str, canonical_label: str, alias_id: str, note: str = "", path: Path | None = None) -> None:
    """Records that `alias_id` is the same person as `canonical_id`. Keeps the file free of chains:
    if `canonical_id` is itself an alias it is resolved first, and anything that pointed at `alias_id`
    now points at the final canonical. Written atomically (temp file + replace)."""
    path = path or ALIASES_PATH
    if canonical_id == alias_id:
        raise ValueError("an author cannot be an alias of itself")
    merges = _read(path)
    # resolve the canonical through existing merges
    for m in merges:
        if canonical_id in m["aliases"]:
            canonical_id, canonical_label = m["canonical"], m["label"]
            break
    if canonical_id == alias_id:
        raise ValueError("these two are already the same author")
    # whatever was merged INTO the new alias now goes to the canonical
    inherited: list[str] = []
    kept = []
    for m in merges:
        if m["canonical"] == alias_id:
            inherited += m["aliases"]
        else:
            kept.append(m)
    merges = kept
    target = next((m for m in merges if m["canonical"] == canonical_id), None)
    if target is None:
        target = {"canonical": canonical_id, "label": canonical_label, "aliases": [],
                  "confirmed": datetime.now().isoformat(timespec="seconds"), "note": note}
        merges.append(target)
    for a in [alias_id, *inherited]:
        if a not in target["aliases"] and a != canonical_id:
            target["aliases"].append(a)
    if note:
        target["note"] = (target.get("note", "") + " | " + note).strip(" |") if target.get("note") else note

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"merges": merges}, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    _cache["key"] = None
