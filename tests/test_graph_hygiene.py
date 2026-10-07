"""Tests for memory/graph_hygiene.py and memory/author_aliases.py — author look-alikes in the knowledge graph.
No Ollama, no KeyBERT (test papers carry no abstract). Everything runs on temporary graphs and a temporary
alias file; the real graph.sqlite is opened read-only in one test and never written.

Pinned: the candidate rule never proposes a different given name; a merge moves every edge and leaves no
self-link, duplicate or orphan; a rebuild that knows the alias produces the same author edges as merging after
the fact (that equality is what makes the recorded decision trustworthy); nothing changes without --yes; and
the decision model only annotates.

Run with: python tests/test_graph_hygiene.py
"""
import io
import json
import sqlite3
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core.decision_client import NimbleUnavailable
from memory import author_aliases, graph_hygiene as gh
from memory.knowledge_graph import ensure_graph_schema, fold_text, ingest_paper_entry

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        _FAILURES.append(label)


def aid(name: str) -> str:
    return f"author:{fold_text(name)}"


def new_graph(papers: list[tuple[str, str, str]]) -> sqlite3.Connection:
    """papers: (arxiv id, title, 'A, B, C')."""
    conn = sqlite3.connect(":memory:")
    ensure_graph_schema(conn)
    for pid, title, authors in papers:
        ingest_paper_entry(conn, {"arXiv ID": pid, "Title": title, "Authors": authors})
    conn.commit()
    return conn


def edge_set(conn):
    return {(s, t, r) for s, t, r in conn.execute("SELECT source_id, target_id, relation_type FROM edges")}


class TempAliases:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = author_aliases.ALIASES_PATH
        author_aliases.ALIASES_PATH = Path(self.tmp.name) / "author_aliases.json"
        author_aliases._cache["key"] = None
        return author_aliases.ALIASES_PATH

    def __exit__(self, *exc):
        author_aliases.ALIASES_PATH = self.old
        author_aliases._cache["key"] = None
        self.tmp.cleanup()


PAPERS = [
    ("1.0001", "Sequence models", "Quoc V. Le, Ilya Sutskever, Oriol Vinyals"),
    ("1.0002", "Neural architecture search", "Quoc Le, Barret Zoph"),
    ("1.0003", "Other work", "Ilya Sutskever, Oriol Vinyals, Chen Chen"),
    ("1.0004", "Different Chen", "Zhang Chen, Chen Chen"),
]


# --- 1. the candidate rule -----------------------------------------------------------------------------
def test_rule_true_duplicates():
    for a, b in (("Quoc Le", "Quoc V. Le"), ("Geoffrey E. Hinton", "Geoffrey Hinton"), ("Peter Battaglia", "Peter W. Battaglia"),
                 ("Tom B. Brown", "Tom Brown"), ("Vishnu Boddeti", "Vishnu Naresh Boddeti"),
                 ("A. Vaswani", "Ashish Vaswani"), ("Łukasz Kaiser", "Lukasz M. Kaiser")):
        check(f"candidate: {a!r} ~ {b!r}", gh.compatible(a, b) is not None and gh.compatible(b, a) is not None)


def test_rule_different_people():
    for a, b in (("Chia Yu Li", "Yu Li"), ("Chao Yang", "Chao-Han Huck Yang"), ("Yuanzhi Li", "Yu Li"), ("Chen Chen", "Zhang Chen"),
                 ("Wei Zhang", "Weidong Zhang"), ("Tom B. Brown", "Tom C. Brown"), ("John Smith", "Jane Smith"),
                 ("Quoc Le", "Quoc Lee"), ("Yu Li", "Yu Li")):
        check(f"not a candidate: {a!r} / {b!r}", gh.compatible(a, b) is None)


def test_rule_edge_cases():
    check("a one-word name is never a candidate", gh.compatible("Plato", "Plato Smith") is None)
    check("initial-only first name is a candidate but flagged", "initial" in (gh.compatible("A. Vaswani", "Ashish Vaswani") or ""))
    check("accents and case are folded", gh.compatible("José García", "Jose M. Garcia") is not None)
    check("middle initial vs full middle name is compatible", gh.compatible("Anna B. Chen", "Anna Beth Chen") is not None)
    check("middle initials that disagree are not", gh.compatible("Anna B. Chen", "Anna C. Chen") is None)


# --- 2. candidates on a graph -----------------------------------------------------------------------------
def test_candidates_and_evidence():
    conn = new_graph(PAPERS)
    cands = gh.find_candidates(conn)
    check("exactly one pair found (Quoc Le / Quoc V. Le); Chen Chen / Zhang Chen is not one", len(cands) == 1)
    c = cands[0]
    check("the fuller name is proposed as the one to keep", c.canonical_label == "Quoc V. Le" and c.alias_label == "Quoc Le")
    check("evidence: 1 paper each, 0 shared; co-authors counted", c.papers == (1, 1) and c.shared_papers == 0 and c.coauthors[1] == 1)
    check("the record given to the model names papers and co-authors", "Sequence models" in c.record_canonical and "Barret Zoph" in c.record_alias)


# --- 3. the merge ------------------------------------------------------------------------------------------
def test_apply_merge():
    conn = new_graph(PAPERS)
    before_authors = conn.execute("SELECT COUNT(*) FROM nodes WHERE node_type='author'").fetchone()[0]
    result = gh.apply_merge(conn, aid("Quoc V. Le"), aid("Quoc Le"))
    conn.commit()
    check("the alias node is gone", conn.execute("SELECT 1 FROM nodes WHERE id=?", (aid("Quoc Le"),)).fetchone() is None)
    check("one author node fewer", conn.execute("SELECT COUNT(*) FROM nodes WHERE node_type='author'").fetchone()[0] == before_authors - 1)
    edges = edge_set(conn)
    check("no edge mentions the removed node", not any(aid("Quoc Le") in (s, t) for s, t, _ in edges))
    check("its paper is now written by the kept author", ("1.0002", aid("Quoc V. Le"), "written_by") in edges)
    zoph = aid("Barret Zoph")
    ordered = tuple(sorted((aid("Quoc V. Le"), zoph)))
    check("its co-author link now points at the kept author, in sorted orientation", (*ordered, "co_authored_with") in edges)
    check("no self-links", all(s != t for s, t, _ in edges))
    check("nothing else changed (Chen Chen's edges intact)", ("1.0003", aid("Chen Chen"), "written_by") in edges and ("1.0004", aid("Chen Chen"), "written_by") in edges)
    check("the counts report what moved", result["edges_moved"] >= 2)


def test_merge_of_authors_that_already_co_authored():
    conn = new_graph([("2.1", "Joint", "Quoc V. Le, Quoc Le, Sam Lee"), ("2.2", "Solo", "Quoc Le, Sam Lee")])
    # both spellings on one paper: they are co-authors of each other (a self-link after the merge)
    check("setup: the two nodes are linked as co-authors", any({aid("Quoc V. Le"), aid("Quoc Le")} == {s, t} for s, t, r in edge_set(conn) if r == "co_authored_with"))
    gh.apply_merge(conn, aid("Quoc V. Le"), aid("Quoc Le"))
    edges = edge_set(conn)
    check("the link between the two becomes nothing, not a self-loop", all(s != t for s, t, _ in edges))
    check("duplicates are collapsed (one written_by per paper and author)", len([e for e in edges if e[2] == "written_by" and e[0] == "2.1" and e[1] == aid("Quoc V. Le")]) == 1)


def test_merge_refuses_bad_input():
    conn = new_graph(PAPERS)
    for label, args in (("itself", (aid("Quoc Le"), aid("Quoc Le"))), ("a missing node", (aid("Quoc Le"), "author:nobody")),
                        ("a paper node", (aid("Quoc Le"), "1.0001"))):
        try:
            gh.apply_merge(conn, *args)
            check(f"refuses to merge {label}", False)
        except ValueError:
            check(f"refuses to merge {label}", True)


# --- 4. the alias file --------------------------------------------------------------------------------------
def test_alias_file():
    with TempAliases() as path:
        check("no file -> no aliases", author_aliases.load() == {})
        author_aliases.add_merge("author:quoc v. le", "Quoc V. Le", "author:quoc le", note="test")
        data = json.loads(path.read_text(encoding="utf-8"))
        check("the merge is written with the label and a timestamp", data["merges"][0]["label"] == "Quoc V. Le" and data["merges"][0]["confirmed"])
        check("lookup resolves the alias", author_aliases.lookup("author:quoc le") == ("author:quoc v. le", "Quoc V. Le"))
        check("the kept author is not an alias", author_aliases.lookup("author:quoc v. le") is None)
        try:
            author_aliases.add_merge("author:x", "X", "author:x")
            check("an author cannot be its own alias", False)
        except ValueError:
            check("an author cannot be its own alias", True)
        # chains are flattened
        author_aliases.add_merge("author:quoc v. le", "Quoc V. Le", "author:q. le")
        author_aliases.add_merge("author:quoc vinh le", "Quoc Vinh Le", "author:quoc v. le")
        m = author_aliases.load()
        check("merging the kept author into another moves everything to the final one",
              m["author:quoc le"][0] == "author:quoc vinh le" and m["author:q. le"][0] == "author:quoc vinh le" and m["author:quoc v. le"][0] == "author:quoc vinh le")
        check("no alias points at another alias", all(v[0] not in m for v in m.values()))


def test_alias_file_broken_never_crashes():
    with TempAliases() as path:
        path.write_text("{ not json", encoding="utf-8")
        check("a broken file is ignored, not fatal", author_aliases.load() == {})
        path.write_text(json.dumps({"merges": [{"canonical": "a"}, "junk"]}), encoding="utf-8")
        author_aliases._cache["key"] = None
        check("malformed entries are skipped", author_aliases.load() == {})


# --- 5. a rebuild that knows the alias == merging after the fact -------------------------------------------------
def test_rebuild_with_alias_equals_merge_afterwards():
    merged = new_graph(PAPERS)
    gh.apply_merge(merged, aid("Quoc V. Le"), aid("Quoc Le"))
    merged.commit()
    with TempAliases():
        author_aliases.add_merge(aid("Quoc V. Le"), "Quoc V. Le", aid("Quoc Le"))
        rebuilt = new_graph(PAPERS)
        check("same edges", edge_set(rebuilt) == edge_set(merged))
        check("same nodes", {r for r in rebuilt.execute("SELECT id, label, node_type FROM nodes")} == {r for r in merged.execute("SELECT id, label, node_type FROM nodes")})


def test_ingest_creates_the_kept_node_when_only_the_alias_appears():
    with TempAliases():
        author_aliases.add_merge(aid("Quoc V. Le"), "Quoc V. Le", aid("Quoc Le"))
        conn = new_graph([("3.1", "Only alias spelling", "Quoc Le, Sam Lee")])
        row = conn.execute("SELECT label FROM nodes WHERE id=?", (aid("Quoc V. Le"),)).fetchone()
        check("the kept node exists with its label even though only the other spelling was ingested", row and row[0] == "Quoc V. Le")
        check("no node for the alias spelling", conn.execute("SELECT 1 FROM nodes WHERE id=?", (aid("Quoc Le"),)).fetchone() is None)
        check("both spellings on one paper give one author and no self-link",
              all(s != t for s, t, _ in edge_set(new_graph([("3.2", "Both", "Quoc Le, Quoc V. Le")]))))


# --- 6. the command line ------------------------------------------------------------------------------------------
def _db_file(tmp: str) -> str:
    path = str(Path(tmp) / "g.sqlite")
    conn = sqlite3.connect(path)
    ensure_graph_schema(conn)
    for pid, title, authors in PAPERS:
        ingest_paper_entry(conn, {"arXiv ID": pid, "Title": title, "Authors": authors})
    conn.commit()
    conn.close()
    return path


def _run(args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = gh.main(args)
    return rc, buf.getvalue()


def test_cli_report_is_read_only():
    with tempfile.TemporaryDirectory() as tmp, TempAliases() as apath:
        db = _db_file(tmp)
        before = Path(db).read_bytes()
        rc, out = _run(["--db", db])
        check("the report lists the pair and the exact command to merge it", rc == 0 and "Quoc V. Le  <-  Quoc Le" in out and "--merge" in out)
        check("the report changes neither the graph nor the alias file", Path(db).read_bytes() == before and not apath.exists())


def test_cli_merge_needs_yes():
    with tempfile.TemporaryDirectory() as tmp, TempAliases() as apath:
        db = _db_file(tmp)
        before = Path(db).read_bytes()
        rc, out = _run(["--db", db, "--merge", "Quoc V. Le", "Quoc Le"])
        check("without --yes it is a dry run", rc == 0 and "Dry run" in out)
        check("...and nothing was changed", Path(db).read_bytes() == before and not apath.exists())
        rc, out = _run(["--db", db, "--merge", "quoc v. le", "QUOC LE", "--yes"])
        conn = sqlite3.connect(db)
        gone = conn.execute("SELECT 1 FROM nodes WHERE id=?", (aid("Quoc Le"),)).fetchone() is None
        conn.close()
        check("with --yes (names are case-insensitive) the graph is merged and the decision recorded",
              rc == 0 and gone and author_aliases.lookup(aid("Quoc Le")) == (aid("Quoc V. Le"), "Quoc V. Le"))
        rc, out = _run(["--db", db])
        check("the merged pair is no longer reported", "No author pairs" in out)


def test_cli_unknown_names_change_nothing():
    with tempfile.TemporaryDirectory() as tmp, TempAliases() as apath:
        db = _db_file(tmp)
        before = Path(db).read_bytes()
        try:
            _run(["--db", db, "--merge", "Nobody Here", "Quoc Le", "--yes"])
            check("an unknown name stops the command", False)
        except SystemExit:
            check("an unknown name stops the command", True)
        check("...and nothing was changed", Path(db).read_bytes() == before and not apath.exists())


def test_failed_alias_write_rolls_the_graph_back():
    with tempfile.TemporaryDirectory() as tmp, TempAliases():
        db = _db_file(tmp)
        before = Path(db).read_bytes()
        author_aliases.ALIASES_PATH = Path(tmp) / "no_such_dir" / "x" / "aliases.json"
        real_mkdir = Path.mkdir
        Path.mkdir = lambda *a, **k: (_ for _ in ()).throw(OSError("disk full"))  # type: ignore[assignment]
        try:
            try:
                _run(["--db", db, "--merge", "Quoc V. Le", "Quoc Le", "--yes"])
                check("an alias-file failure surfaces", False)
            except OSError:
                check("an alias-file failure surfaces", True)
        finally:
            Path.mkdir = real_mkdir  # type: ignore[assignment]
        conn = sqlite3.connect(db)
        still = conn.execute("SELECT 1 FROM nodes WHERE id=?", (aid("Quoc Le"),)).fetchone() is not None
        conn.close()
        check("...and the graph was not merged", still and Path(db).read_bytes() == before)


# --- 7. the model only annotates ------------------------------------------------------------------------------
def fake(choice, p_same):
    return lambda state, questions: {"same": {"type": "choice", "choice": choice, "probabilities": {"same_person": p_same}}}


def test_opinion_is_only_an_annotation():
    conn = new_graph(PAPERS)
    c = gh.find_candidates(conn)[0]
    check("opinion returns the choice and P(same)", gh.ask_opinion(c, ask=fake("same_person", 0.97)) == ("same_person", 0.97))
    c.opinion = ("same_person", 0.97)
    buf = io.StringIO()
    with redirect_stdout(buf):
        gh._print_report([c], True)
    check("a confident 'same' is shown as a hint", "merge looks right" in buf.getvalue())
    c.opinion = ("different_people", 0.10)
    buf = io.StringIO()
    with redirect_stdout(buf):
        gh._print_report([c], True)
    check("a doubtful one says to review", "review carefully" in buf.getvalue())
    c.opinion = ("same_person", 0.80)
    buf = io.StringIO()
    with redirect_stdout(buf):
        gh._print_report([c], True)
    check("'same' below the hint threshold still says to review", "review carefully" in buf.getvalue())
    check("nothing about the opinion changes the graph: it is only printed", conn.execute("SELECT COUNT(*) FROM nodes WHERE id=?", (aid("Quoc Le"),)).fetchone()[0] == 1)


def test_cli_with_model_unavailable():
    import core.memory_proposals  # noqa: F401  (loads the shared client the way the app does)
    with tempfile.TemporaryDirectory() as tmp, TempAliases():
        db = _db_file(tmp)
        original = gh.ask_opinion
        gh.ask_opinion = lambda c, ask=None: (_ for _ in ()).throw(NimbleUnavailable("HTTP 404"))  # type: ignore[assignment]
        try:
            rc, out = _run(["--db", db, "--ask-nimble"])
        finally:
            gh.ask_opinion = original  # type: ignore[assignment]
        check("without the model the report still appears, with a note", rc == 0 and "nimble unavailable" in out and "Quoc V. Le" in out)


# --- 8. the real graph, read only ------------------------------------------------------------------------------
def test_real_graph_read_only():
    db = Path(__file__).resolve().parent.parent / "memory" / "store" / "graph.sqlite"
    if not db.exists():
        print("[SKIP] real graph not present")
        return
    conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    labels = {r[0] for r in conn.execute("SELECT label FROM nodes WHERE node_type='author'")}
    found = {(c.canonical_label, c.alias_label) for c in gh.find_candidates(conn)}
    for keep, alias in (("Quoc V. Le", "Quoc Le"), ("Geoffrey E. Hinton", "Geoffrey Hinton"), ("Peter W. Battaglia", "Peter Battaglia"),
                        ("Tom B. Brown", "Tom Brown"), ("Vishnu Naresh Boddeti", "Vishnu Boddeti")):
        if keep in labels and alias in labels:
            check(f"real graph: {alias!r} -> {keep!r} is found", (keep, alias) in found)
    for a, b in (("Chia Yu Li", "Yu Li"), ("Chao Yang", "Chao-Han Huck Yang")):
        check(f"real graph: {a!r} / {b!r} is not proposed", not any({a, b} == {k, al} for k, al in found))
    check("real graph: a short review list, not hundreds", len(found) <= 15)
    conn.close()


if __name__ == "__main__":
    test_rule_true_duplicates()
    test_rule_different_people()
    test_rule_edge_cases()
    test_candidates_and_evidence()
    test_apply_merge()
    test_merge_of_authors_that_already_co_authored()
    test_merge_refuses_bad_input()
    test_alias_file()
    test_alias_file_broken_never_crashes()
    test_rebuild_with_alias_equals_merge_afterwards()
    test_ingest_creates_the_kept_node_when_only_the_alias_appears()
    test_cli_report_is_read_only()
    test_cli_merge_needs_yes()
    test_cli_unknown_names_change_nothing()
    test_failed_alias_write_rolls_the_graph_back()
    test_opinion_is_only_an_annotation()
    test_cli_with_model_unavailable()
    test_real_graph_read_only()
    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} check(s) FAILED:")
        for f in _FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("All checks passed.")
