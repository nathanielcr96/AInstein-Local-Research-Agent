"""Finds author nodes of the knowledge graph that may be the same person, and merges the ones a person confirms.

    python -m memory.graph_hygiene                       # read-only report
    python -m memory.graph_hygiene --ask-nimble          # ...with the decision model's opinion on each pair
    python -m memory.graph_hygiene --merge "Quoc V. Le" "Quoc Le"          # dry run: shows what would change
    python -m memory.graph_hygiene --merge "Quoc V. Le" "Quoc Le" --yes    # applies it

Why it exists (README, "Graph construction has real limits"): an author is identified by their folded name
alone, so the same researcher with and without a middle initial becomes two nodes. On the graph this was
written against, 5 of 811 authors were such pairs; the other look-alikes (Yu Li / Yujia Li, Chen Chen ...) are
different people.

Three layers, safety first:
  1. Candidates come from a deterministic rule — same surname, same first name (or an initial of it), middle
     names that only add to each other. A different first name is never a candidate ("Chia Yu Li" is not "Yu Li").
  2. `--ask-nimble` only ANNOTATES each candidate with the decision model's opinion. It never acts. On the 7 real
     pairs it was tried on it was right 7/7, but only 0.50-0.74 sure about the two different people, so it is a
     hint for the person reviewing, not a decision.
  3. A merge needs an explicit command (dry run unless `--yes`). A wrong merge is the one that is hard to
     undo, and a name shared by two researchers cannot be told apart from the graph alone.

A confirmed merge is written to memory/store/author_aliases.json (see memory/author_aliases.py), which the graph
builder consults on every ingest, so a rebuild keeps it. To undo one: delete its entry there and rebuild
(`python -m memory.knowledge_graph`).
"""
import argparse
import logging
import sqlite3
import sys
from dataclasses import dataclass, field

from core import decision_client
from core.decision_client import NimbleUnavailable
from memory import author_aliases
from memory.knowledge_graph import GRAPH_DB_PATH, fold_text, upsert_edge

logger = logging.getLogger(__name__)

SAME_PERSON_HINT = 0.9  # P(same_person) at or above which the report says "merge looks right"

SAME_QUESTION = {
    "type": "choice",
    "instructions": "Are these two author records the same person?",
    "criteria": {
        "same_person": "Same person: the names differ only by middle names or initials and the papers and co-authors fit one researcher",
        "different_people": "Different people: the names, papers or co-authors point to two different researchers",
        "cannot_tell": "The records do not give enough evidence either way",
    },
}


# ---------------------------------------------------------------- 1. deterministic candidates
def name_tokens(label: str) -> list[str]:
    """Folded name split on whitespace. Periods go, hyphens stay: 'Chao-Han' is one given name, not two."""
    return fold_text(label).replace(".", " ").split()


def _initial_or_equal(a: str, b: str) -> bool:
    return a == b or (len(a) == 1 and b.startswith(a)) or (len(b) == 1 and a.startswith(b))


def _middles_compatible(x: list[str], y: list[str]) -> bool:
    """The shorter middle-name list must fit, in order, inside the longer one (equal, or one is an initial of
    the other). ['v'] fits ['vincent']; ['e'] does not fit ['b']; [] fits anything."""
    short, long_ = (x, y) if len(x) <= len(y) else (y, x)
    i = 0
    for tok in long_:
        if i < len(short) and _initial_or_equal(short[i], tok):
            i += 1
    return i == len(short)


def compatible(label_a: str, label_b: str) -> str | None:
    """None if the two names cannot be the same person by this rule, else a short note on why they might be."""
    x, y = name_tokens(label_a), name_tokens(label_b)
    if len(x) < 2 or len(y) < 2 or x == y:
        return None
    if x[-1] != y[-1]:  # surnames must match exactly
        return None
    if not _initial_or_equal(x[0], y[0]):  # a different given name is a different person
        return None
    if not _middles_compatible(x[1:-1], y[1:-1]):
        return None
    if x[0] != y[0]:
        return "first name given only as an initial in one of them"
    if len(x) == len(y):
        return "middle names given as initial in one of them"
    return "one has a middle name or initial the other lacks"


@dataclass
class Candidate:
    canonical_id: str
    canonical_label: str
    alias_id: str
    alias_label: str
    note: str
    papers: tuple[int, int]        # (canonical, alias)
    coauthors: tuple[int, int]
    shared_papers: int
    shared_coauthors: int
    record_canonical: str = ""
    record_alias: str = ""
    opinion: tuple[str, float] | None = None  # (choice, P(same_person)) from --ask-nimble
    extra: dict = field(default_factory=dict)


def _papers(conn: sqlite3.Connection, author_id: str) -> list[tuple[str, str]]:
    return conn.execute(
        "SELECT n.id, n.label FROM edges e JOIN nodes n ON n.id = e.source_id "
        "WHERE e.relation_type = 'written_by' AND e.target_id = ?", (author_id,)).fetchall()


def _coauthors(conn: sqlite3.Connection, author_id: str) -> list[tuple[str, str]]:
    return conn.execute(
        "SELECT n.id, n.label FROM edges e JOIN nodes n ON n.id = CASE WHEN e.source_id = ? THEN e.target_id ELSE e.source_id END "
        "WHERE e.relation_type = 'co_authored_with' AND (e.source_id = ? OR e.target_id = ?)",
        (author_id, author_id, author_id)).fetchall()


def _record(label: str, papers: list[tuple[str, str]], coauthors: list[tuple[str, str]]) -> str:
    return (f"{label}. Papers: {'; '.join(p[1][:90] for p in papers[:3])}. "
            f"Co-authors: {', '.join(c[1] for c in coauthors[:6])}.")


def find_candidates(conn: sqlite3.Connection) -> list[Candidate]:
    authors = conn.execute("SELECT id, label FROM nodes WHERE node_type = 'author'").fetchall()
    by_surname: dict[str, list[tuple[str, str]]] = {}
    for aid, label in authors:
        toks = name_tokens(label)
        if len(toks) >= 2:
            by_surname.setdefault(toks[-1], []).append((aid, label))

    out: list[Candidate] = []
    for group in by_surname.values():
        for i, (id_a, lab_a) in enumerate(group):
            for id_b, lab_b in group[i + 1:]:
                note = compatible(lab_a, lab_b)
                if note is None:
                    continue
                pa, pb = _papers(conn, id_a), _papers(conn, id_b)
                ca, cb = _coauthors(conn, id_a), _coauthors(conn, id_b)
                # canonical = the fuller name (more tokens), then the one with more papers
                a_first = (len(name_tokens(lab_a)), len(pa)) >= (len(name_tokens(lab_b)), len(pb))
                (cid, clab, cp, cc), (aid, alab, ap, ac) = (
                    ((id_a, lab_a, pa, ca), (id_b, lab_b, pb, cb)) if a_first else ((id_b, lab_b, pb, cb), (id_a, lab_a, pa, ca)))
                out.append(Candidate(
                    canonical_id=cid, canonical_label=clab, alias_id=aid, alias_label=alab, note=note,
                    papers=(len(cp), len(ap)), coauthors=(len(cc), len(ac)),
                    shared_papers=len({p[0] for p in cp} & {p[0] for p in ap}),
                    shared_coauthors=len({c[0] for c in cc} & {c[0] for c in ac}),
                    record_canonical=_record(clab, cp, cc), record_alias=_record(alab, ap, ac),
                ))
    return sorted(out, key=lambda c: (c.canonical_label.lower(), c.alias_label.lower()))


# ---------------------------------------------------------------- 2. the model's opinion (annotation only)
def ask_opinion(c: Candidate, ask=decision_client.ask) -> tuple[str, float]:
    """(choice, P(same_person)). Raises NimbleUnavailable when the model can't be reached."""
    ans = ask({"author_a": c.record_canonical, "author_b": c.record_alias}, {"same": SAME_QUESTION})["same"]
    return ans["choice"], float(ans.get("probabilities", {}).get("same_person", 0.0))


# ---------------------------------------------------------------- 3. the merge
def _author_node(conn: sqlite3.Connection, node_id: str) -> tuple[str, str]:
    row = conn.execute("SELECT label, node_type FROM nodes WHERE id = ?", (node_id,)).fetchone()
    if row is None:
        raise ValueError(f"no node with id {node_id!r}")
    if row[1] != "author":
        raise ValueError(f"{node_id!r} is a {row[1]} node, not an author")
    return row[0], row[1]


def apply_merge(conn: sqlite3.Connection, canonical_id: str, alias_id: str) -> dict:
    """Moves every edge of `alias_id` to `canonical_id` and deletes the alias node — what a rebuild with the
    alias recorded would have produced. Does NOT commit: the caller commits once the alias file is written.
    Edges that would become a self-loop or a duplicate are dropped; co_authored_with keeps its sorted
    orientation (that is how ingest stores it)."""
    if canonical_id == alias_id:
        raise ValueError("cannot merge an author into itself")
    _author_node(conn, canonical_id)
    _author_node(conn, alias_id)

    moved = dropped = 0
    rows = conn.execute(
        "SELECT id, source_id, target_id, relation_type, weight, source FROM edges WHERE source_id = ? OR target_id = ?",
        (alias_id, alias_id)).fetchall()
    for edge_id, s, t, rel, weight, src in rows:
        conn.execute("DELETE FROM edges WHERE id = ?", (edge_id,))
        s2 = canonical_id if s == alias_id else s
        t2 = canonical_id if t == alias_id else t
        if s2 == t2:
            dropped += 1
            continue
        if rel == "co_authored_with":
            s2, t2 = sorted((s2, t2))
        existed = conn.execute(
            "SELECT 1 FROM edges WHERE source_id = ? AND target_id = ? AND relation_type = ?", (s2, t2, rel)).fetchone()
        upsert_edge(conn, s2, t2, rel, weight, src)
        if existed:
            dropped += 1
        else:
            moved += 1
    conn.execute("DELETE FROM nodes WHERE id = ?", (alias_id,))
    return {"edges_moved": moved, "edges_dropped": dropped}


def _resolve_author(conn: sqlite3.Connection, name: str) -> tuple[str, str]:
    rows = conn.execute(
        "SELECT id, label FROM nodes WHERE node_type = 'author' AND (lower(label) = lower(?) OR id = ?)", (name, name)).fetchall()
    if not rows:
        raise SystemExit(f"No author named {name!r} in the graph.")
    if len(rows) > 1:
        raise SystemExit(f"{name!r} matches several authors: {[r[1] for r in rows]}. Use the node id instead.")
    return rows[0]


# ---------------------------------------------------------------- CLI
def _print_report(candidates: list[Candidate], ask_nimble: bool) -> None:
    if not candidates:
        print("No author pairs to review.")
        return
    print(f"{len(candidates)} author pair(s) that may be the same person (deterministic rule; nothing is changed):\n")
    for n, c in enumerate(candidates, 1):
        evidence = (f"papers {c.papers[0]}/{c.papers[1]} (shared {c.shared_papers}), "
                    f"co-authors {c.coauthors[0]}/{c.coauthors[1]} (shared {c.shared_coauthors})")
        print(f"{n}. {c.canonical_label}  <-  {c.alias_label}   [{c.note}]")
        print(f"   {evidence}")
        if c.opinion:
            choice, p = c.opinion
            verdict = "merge looks right" if choice == "same_person" and p >= SAME_PERSON_HINT else "review carefully"
            print(f"   nimble: {choice} (P(same)={p:.2f}) -> {verdict}")
        print(f'   to merge: python -m memory.graph_hygiene --merge "{c.canonical_label}" "{c.alias_label}"\n')


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ask-nimble", action="store_true", help="annotate each pair with the decision model's opinion (one call per pair)")
    ap.add_argument("--merge", nargs=2, metavar=("KEEP", "ALIAS"), help="merge ALIAS into KEEP (names or node ids); dry run unless --yes")
    ap.add_argument("--yes", action="store_true", help="actually apply --merge")
    ap.add_argument("--db", default=str(GRAPH_DB_PATH), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # a redirected stdout (tests, pipes into StringIO) has none
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    conn = sqlite3.connect(args.db, timeout=30)
    try:
        if args.merge:
            keep_id, keep_label = _resolve_author(conn, args.merge[0])
            alias_id, alias_label = _resolve_author(conn, args.merge[1])
            print(f"Merge {alias_label!r} into {keep_label!r}: all its papers and co-author links move to {keep_label!r},")
            print(f"the node {alias_label!r} is removed, and the choice is recorded in {author_aliases.ALIASES_PATH.name} "
                  "so a graph rebuild keeps it.")
            try:
                result = apply_merge(conn, keep_id, alias_id)
                print(f"  edges moved: {result['edges_moved']}, dropped (duplicate or self-link): {result['edges_dropped']}")
                if not args.yes:
                    conn.rollback()
                    print("\nDry run: nothing was changed. Add --yes to apply.")
                    return 0
                author_aliases.add_merge(keep_id, keep_label, alias_id, note=f"merged {alias_label!r} into {keep_label!r}")
                conn.commit()
                print("\nDone.")
                return 0
            except Exception:
                conn.rollback()
                raise

        candidates = find_candidates(conn)
        if args.ask_nimble:
            for c in candidates:
                try:
                    c.opinion = ask_opinion(c)
                except NimbleUnavailable as e:
                    print(f"(nimble unavailable: {e} - showing the report without its opinion)\n")
                    break
        _print_report(candidates, args.ask_nimble)
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
