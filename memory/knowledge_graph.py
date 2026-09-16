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

import sqlite3
from itertools import combinations
from pathlib import Path

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util

from memory.memory_tools import MEMORY_FILE, _list_memory_entries, _parse_kv_block

GRAPH_DB_PATH = (Path(__file__).parent / "store" / "graph.sqlite").resolve()

_KEYWORDS_PER_PAPER = 5

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


def _normalize_author(name: str) -> str:
    return " ".join(name.strip().split())


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

    authors = [_normalize_author(a) for a in fields.get("Authors", "").split(",") if a.strip()]

    for author in authors:
        author_id = f"author:{author}"
        upsert_node(conn, author_id, author, "author")
        upsert_edge(conn, paper_id, author_id, "written_by", 1.0, "long_term_memory")

    for a, b in combinations(sorted(authors), 2):
        upsert_edge(conn, f"author:{a}", f"author:{b}", "co_authored_with", 1.0, "long_term_memory")

    categories = [c.strip() for c in fields.get("Categories", "").split(",") if c.strip()]

    for category in categories:
        category_id = f"keyword:{category.lower()}"
        upsert_node(conn, category_id, category, "keyword")
        upsert_edge(conn, paper_id, category_id, "has_category", 1.0, "arxiv")

    abstract = fields.get("Abstract", "")

    if abstract:
        keywords = _get_keyword_model().extract_keywords(
            abstract, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=_KEYWORDS_PER_PAPER
        )
        for phrase, score in keywords:
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


def backfill_from_long_term_memory() -> dict:
    """One-off ingestion of every `paper` entry already in
    memory/store/long_term.md into graph.sqlite. Safe to re-run any time
    (new papers get added later, backfill again) — upsert_node/upsert_edge
    are idempotent, never produce duplicates.
    """

    if not MEMORY_FILE.exists():
        return {"papers_ingested": 0, "nodes": 0, "edges": 0, "keyword_similarity_edges": 0}

    text = MEMORY_FILE.read_text(encoding="utf-8")
    paper_entries = [e for e in _list_memory_entries(text) if e["category"] == "paper"]

    GRAPH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(GRAPH_DB_PATH))
    ensure_graph_schema(conn)

    ingested = 0

    for entry in paper_entries:
        fields = _parse_kv_block(entry["content"])
        if ingest_paper_entry(conn, fields):
            ingested += 1

    conn.commit()

    keyword_edges = compute_keyword_similarity_edges(conn)
    conn.commit()

    node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]

    conn.close()

    return {
        "papers_ingested": ingested,
        "nodes": node_count,
        "edges": edge_count,
        "keyword_similarity_edges": keyword_edges,
    }


if __name__ == "__main__":
    print(backfill_from_long_term_memory())
