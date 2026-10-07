"""Unified knowledge graph over papers/authors/keywords — one graph with
several node types and relation types, not separate graphs per entity.
Settled explicitly: a question like "what topics does author X work on"
needs a two-hop traversal through `paper` (author -> paper -> keyword), so
papers/authors/keywords have to share one graph — splitting them would
mean duplicating `paper` nodes across graphs as a bridge, which is worse
than just keeping one graph with a `node_type` column.

Filled deterministically, same principle as PaperMemoryMiddleware
(core/middleware.py): nothing here depends on a model deciding to call a
tool. Two ways in, sharing the same per-paper logic:
- `backfill_from_long_term_memory()`: one-off pass over every existing
  `paper` entry already in memory/store/long_term.md. Run directly:
  `python -m memory.knowledge_graph`.
- `ingest_paper_entry(conn, fields)`: the same logic, meant to be called
  from a middleware later so new papers join the graph live instead of
  only at backfill time — not wired up yet, this module is the shared
  core both will use.

Keyword-to-keyword edges come from embedding similarity, not a
model-asserted hierarchy: deliberately avoids trusting a small model to
classify "RAG relates to LLM more than to AI" (the exact kind of
structural judgment call this project has repeatedly found small local
models unreliable at) — plain cosine similarity between keyword text
embeddings does this instead, and is what actually makes RAG/LLM end up
closer together than RAG/AI once visualized with a force-directed layout.
"""

import re
import sqlite3
import unicodedata
from itertools import combinations
from pathlib import Path

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from memory import author_aliases
from memory.memory_tools import MEMORY_FILE, _list_memory_entries, _parse_kv_block

GRAPH_DB_PATH = (Path(__file__).parent / "store" / "graph.sqlite").resolve()

_KEYWORDS_PER_PAPER = 8

# KeyBERT is asked for more candidates than are kept: most of its noise is
# removed afterwards (see _clean_keyphrases), so asking for exactly
# _KEYWORDS_PER_PAPER would leave papers with too few keywords once the
# junk is filtered out.
_KEYWORD_CANDIDATES_PER_PAPER = _KEYWORDS_PER_PAPER * 4

# Generic abstract-speak that is never a topic on its own. Removed before
# n-grams are formed, alongside sklearn's English stop words.
_KEYWORD_FILLER_WORDS = frozenset({
    "paper", "propose", "proposed", "proposes", "present", "presents", "presented",
    "show", "shows", "shown", "using", "use", "used", "uses", "based", "novel", "new",
    "approach", "approaches", "method", "methods", "result", "results", "work", "works",
    "study", "studies", "also", "however", "thus", "via", "demonstrate", "demonstrates",
    "introduce", "introduces", "achieve", "achieves", "existing", "recent", "various",
    "different", "directly", "effectively", "significantly", "extensive", "experiments",
    "experimental", "including", "address", "provide", "provides", "enable", "enables",
})
_KEYWORD_STOP_WORDS = sorted(ENGLISH_STOP_WORDS | _KEYWORD_FILLER_WORDS)

# Below this cosine similarity, a keyword pair doesn't get a `related_to`
# edge at all — without a floor, embedding two nodes always yields *some*
# nonzero similarity, and a fully connected graph is as useless to look at
# as no graph at all.
_KEYWORD_SIMILARITY_THRESHOLD = 0.45

# Separate from whatever embedding model is chosen for search_memory/
# search_paper_content in the chat settings — this graph is its own
# subsystem, doesn't need to match that choice, and a small CPU-friendly
# model (already a light pull via sentence-transformers, no Ollama call
# needed) is enough for keyword-to-keyword similarity specifically.
_EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

_kw_model: KeyBERT | None = None
_embed_model: SentenceTransformer | None = None


def _get_keyword_model() -> KeyBERT:
    global _kw_model
    if _kw_model is None:
        _kw_model = KeyBERT(model=_EMBEDDING_MODEL_NAME)
    return _kw_model


def _get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(_EMBEDDING_MODEL_NAME)
    return _embed_model


_SPECIAL_FOLD = str.maketrans({
    "ł": "l", "Ł": "L", "ø": "o", "Ø": "O", "đ": "d", "Đ": "D",
    "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE",
})


def fold_text(text: str) -> str:
    """Lowercase, accent-free, whitespace-collapsed form of `text`, used as
    an identity key (authors) and as a search key. NFKD alone doesn't
    decompose letters like ł/ø/đ (they're not "base letter + accent"), so
    those are mapped explicitly — this is what keeps "Łukasz Kaiser" and
    "Lukasz Kaiser" (the same person, spelled differently across arXiv
    records) from becoming two separate author nodes.
    """
    text = unicodedata.normalize("NFKD", text.translate(_SPECIAL_FOLD))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.casefold().split())


def _normalize_author(name: str) -> str:
    return " ".join(name.strip().split())


def _display_score(name: str) -> tuple[int, bool]:
    """Which spelling of the same author to show: the one with more
    non-ASCII characters (diacritics are information the ASCII variant
    lost), then one that isn't all-lowercase.
    """
    return (sum(1 for ch in name if ord(ch) > 127), name != name.lower())


def _upsert_author(conn: sqlite3.Connection, name: str) -> str:
    author_id = f"author:{fold_text(name)}"

    # A person confirmed that this spelling is the same researcher as another node
    # (memory/author_aliases.py): the edges go to that node, and no node is created for this spelling.
    alias = author_aliases.lookup(author_id)
    if alias is not None:
        canonical_id, canonical_label = alias
        if conn.execute("SELECT 1 FROM nodes WHERE id = ?", (canonical_id,)).fetchone() is None:
            upsert_node(conn, canonical_id, canonical_label, "author")
        return canonical_id

    row = conn.execute("SELECT label FROM nodes WHERE id = ?", (author_id,)).fetchone()

    if row is None or _display_score(name) > _display_score(row[0]):
        upsert_node(conn, author_id, name, "author")

    return author_id


_IRREGULAR_SINGULAR_EXCEPTIONS = frozenset({"series", "species", "news", "physics", "statistics", "mathematics"})


def _singularize(word: str) -> str:
    if word in _IRREGULAR_SINGULAR_EXCEPTIONS or len(word) <= 3:
        return word
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("s") and not word.endswith(("ss", "us", "is", "as", "os", "ics")):
        return word[:-1]
    return word


def _canonical_keyphrase(phrase: str) -> str:
    """Only the last word is singularized ("convolutional networks" ->
    "convolutional network"): a noun phrase's plural lives on its head
    noun, and touching earlier words risks mangling adjectives.
    """
    words = phrase.split()
    words[-1] = _singularize(words[-1])
    return " ".join(words)


def _normalize_for_matching(text: str) -> str:
    # Sentence/clause punctuation becomes a "|" barrier no keyphrase can
    # contain, so a bigram can't match across it ("...attention
    # mechanisms. Concrete..." must not validate "mechanisms concrete").
    # Other symbols (hyphens, apostrophes) just become spaces, which keeps
    # "self-attention" matching the phrase "self attention".
    text = re.sub(r"[.,;:!?()\[\]{}\"]", " | ", text.lower())
    return " " + " ".join(re.sub(r"[^a-z0-9|\s]", " ", text).split()) + " "


def _clean_keyphrases(candidates: list[tuple[str, float]], abstract: str) -> list[tuple[str, float]]:
    """Filters KeyBERT's raw candidates down to real phrases from the text.

    The main noise source: stop words are removed *before* n-grams are
    formed, so two words that were never adjacent in the abstract become a
    bigram ("attention directly", "learning reinforcement"). Measured on
    the real corpus: ~30% of all extracted bigrams did not appear
    literally in any abstract. Requiring the phrase to occur verbatim in
    the (normalized) abstract removes exactly that class deterministically.
    """
    haystack = _normalize_for_matching(abstract)
    kept: list[tuple[str, float]] = []
    seen: set[str] = set()

    for phrase, score in candidates:
        words = phrase.split()

        if any(w.isdigit() for w in words) or (len(words) == 1 and len(phrase) < 3):
            continue
        if len(words) == 2 and words[0] == words[1]:
            continue
        if f" {phrase} " not in haystack:
            continue

        canonical = _canonical_keyphrase(phrase)
        if canonical in seen:
            continue

        seen.add(canonical)
        kept.append((canonical, score))

        if len(kept) == _KEYWORDS_PER_PAPER:
            break

    return kept


def ensure_graph_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            node_type TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL REFERENCES nodes(id),
            target_id TEXT NOT NULL REFERENCES nodes(id),
            relation_type TEXT NOT NULL,
            weight REAL NOT NULL DEFAULT 1.0,
            source TEXT NOT NULL,
            UNIQUE(source_id, target_id, relation_type)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id)")
    conn.commit()


def upsert_node(conn: sqlite3.Connection, node_id: str, label: str, node_type: str) -> None:
    conn.execute(
        "INSERT INTO nodes (id, label, node_type) VALUES (?, ?, ?) "
        "ON CONFLICT(id) DO UPDATE SET label = excluded.label",
        (node_id, label, node_type),
    )


def upsert_edge(
    conn: sqlite3.Connection, source_id: str, target_id: str, relation_type: str, weight: float, source: str
) -> None:
    conn.execute(
        "INSERT INTO edges (source_id, target_id, relation_type, weight, source) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(source_id, target_id, relation_type) DO UPDATE SET weight = excluded.weight",
        (source_id, target_id, relation_type, weight, source),
    )


def ingest_paper_entry(conn: sqlite3.Connection, fields: dict) -> str | None:
    """Adds/updates one paper's nodes and edges — paper, authors,
    co-authorship, arXiv categories, extracted keywords — from its parsed
    key:value fields (the same shape PaperMemoryMiddleware already writes
    to long_term.md, reused as-is rather than re-fetched). Returns the
    paper's node id, or None if the fields have no arXiv id to anchor on.
    """

    paper_id = fields.get("arXiv ID")

    if not paper_id:
        return None

    upsert_node(conn, paper_id, fields.get("Title", paper_id), "paper")

    names = [_normalize_author(a) for a in fields.get("Authors", "").split(",") if a.strip()]

    # Deduplicated by identity (accent/case-folded id), not by raw string:
    # the same person listed under two spellings on one record must not
    # produce a co_authored_with self-edge.
    author_ids = sorted({_upsert_author(conn, name) for name in names})

    for author_id in author_ids:
        upsert_edge(conn, paper_id, author_id, "written_by", 1.0, "long_term_memory")

    for a, b in combinations(author_ids, 2):
        upsert_edge(conn, a, b, "co_authored_with", 1.0, "long_term_memory")

    categories = [c.strip() for c in fields.get("Categories", "").split(",") if c.strip()]

    for category in categories:
        category_id = f"keyword:{category.lower()}"
        upsert_node(conn, category_id, category, "keyword")
        upsert_edge(conn, paper_id, category_id, "has_category", 1.0, "arxiv")

    abstract = fields.get("Abstract", "")

    if abstract:
        # MMR (diversity=0.5) so the top candidates aren't near-copies of
        # each other ("attention", "self attention", "attention based"...).
        candidates = _get_keyword_model().extract_keywords(
            abstract,
            keyphrase_ngram_range=(1, 2),
            stop_words=_KEYWORD_STOP_WORDS,
            use_mmr=True,
            diversity=0.5,
            top_n=_KEYWORD_CANDIDATES_PER_PAPER,
        )
        for phrase, score in _clean_keyphrases(candidates, abstract):
            keyword_id = f"keyword:{phrase.lower()}"
            upsert_node(conn, keyword_id, phrase, "keyword")
            upsert_edge(conn, paper_id, keyword_id, "has_keyword", float(score), "keybert")

    return paper_id


def compute_keyword_similarity_edges(conn: sqlite3.Connection, threshold: float = _KEYWORD_SIMILARITY_THRESHOLD) -> int:
    """Adds `related_to` edges between `keyword`-type nodes (both
    KeyBERT-extracted phrases and arXiv categories) whose text embeddings
    are close enough. This is what places a node like "RAG" nearer "LLM"
    than "AI" once the graph is laid out — an emergent property of the
    embedding space, not a hand-written or model-asserted hierarchy.
    """

    rows = conn.execute("SELECT id, label FROM nodes WHERE node_type = 'keyword'").fetchall()

    if len(rows) < 2:
        return 0

    ids = [row[0] for row in rows]
    labels = [row[1] for row in rows]

    embeddings = _get_embed_model().encode(labels, convert_to_tensor=True)
    similarities = util.cos_sim(embeddings, embeddings)

    added = 0

    for i, j in combinations(range(len(ids)), 2):
        score = float(similarities[i][j])
        if score >= threshold:
            upsert_edge(conn, ids[i], ids[j], "related_to", score, "embedding_similarity")
            added += 1

    return added


# Central topics worth guaranteeing a cohesive neighborhood for, beyond
# whatever embedding similarity happens to find on its own. Substring
# match against every keyword label (case-insensitive) rather than an
# exact-label lookup: KeyBERT's own phrase variety means the concept shows
# up as many different literal strings ("query attention", "attention
# transformer", "self attentional", ...), and embedding similarity alone
# doesn't reliably pull ALL of them close to a single "attention" node
# (two phrases can each be attention-related without being close to each
# *other* in embedding space). A plain substring rule is deterministic and
# guarantees the hub actually connects to every variant, rather than
# hoping the embedding geometry happens to cooperate.
HUB_KEYWORDS = ["attention"]


def connect_hub_keywords(conn: sqlite3.Connection, hub_terms: list[str] = HUB_KEYWORDS) -> dict[str, int]:
    """For each term in `hub_terms`, ensures a `keyword` node for that
    exact term exists and adds a `related_to` edge (source="hub_match",
    weight=1.0 — a fixed, maximal weight, not a similarity score) from it
    to every OTHER keyword node whose label contains the term as a
    case-insensitive substring. Idempotent like everything else here.
    """

    added_per_term: dict[str, int] = {}

    for term in hub_terms:
        hub_id = f"keyword:{term.lower()}"
        upsert_node(conn, hub_id, term, "keyword")

        matches = conn.execute(
            "SELECT id FROM nodes WHERE node_type = 'keyword' AND lower(label) LIKE ? AND id != ?",
            (f"%{term.lower()}%", hub_id),
        ).fetchall()

        count = 0
        for (other_id,) in matches:
            upsert_edge(conn, hub_id, other_id, "related_to", 1.0, "hub_match")
            count += 1

        added_per_term[term] = count

    return added_per_term


def backfill_from_long_term_memory() -> dict:
    """Rebuilds graph.sqlite from scratch out of every `paper` entry in
    memory/store/long_term.md (the single source of truth — everything in
    the graph is derived from it), then re-run any time new papers are
    added.

    A full rebuild rather than an incremental upsert on purpose: when the
    extraction rules improve (author identity, keyword filtering), an
    upsert-only pass leaves the old, now-wrong nodes behind forever. The
    whole thing runs in ONE transaction (DELETE ... re-ingest ... commit),
    not by swapping the file: graph_app.py holds a read-only connection to
    graph.sqlite open, and readers keep seeing the previous graph until the
    commit, never a half-built one.
    """

    if not MEMORY_FILE.exists():
        return {"papers_ingested": 0, "nodes": 0, "edges": 0, "keyword_similarity_edges": 0}

    text = MEMORY_FILE.read_text(encoding="utf-8")
    paper_entries = [e for e in _list_memory_entries(text) if e["category"] == "paper"]

    GRAPH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(GRAPH_DB_PATH), timeout=30)
    ensure_graph_schema(conn)

    ingested = 0

    try:
        conn.execute("DELETE FROM edges")
        conn.execute("DELETE FROM nodes")

        for entry in paper_entries:
            fields = _parse_kv_block(entry["content"])
            if ingest_paper_entry(conn, fields):
                ingested += 1

        keyword_edges = compute_keyword_similarity_edges(conn)
        hub_edges = connect_hub_keywords(conn)

        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        raise

    node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]

    conn.close()

    return {
        "papers_ingested": ingested,
        "nodes": node_count,
        "edges": edge_count,
        "keyword_similarity_edges": keyword_edges,
        "hub_edges": hub_edges,
    }


if __name__ == "__main__":
    print(backfill_from_long_term_memory())
