"""Persistent cache of child-chunk embeddings for search_paper_content, in
memory/store/embeddings.sqlite.

Why this exists: the in-memory-only FAISS index (the previous approach,
still used for search_memory where the corpus is small) required embedding
every child chunk on every cold start. With ~14,600 child chunks across 167
papers, a single `embed_documents` call over all of them was verified live
to fail — Ollama's `/api/embed` endpoint errored after ~4.5 minutes, having
processed only part of the batch (roughly 17 chunks/sec on this machine, so
the full set would take ~14 minutes even if it didn't fail outright). This
cache makes that cost one-time per chunk instead of once per process start:
already-embedded chunks are read back from SQLite (fast, no Ollama call),
and only genuinely new chunks (a newly downloaded paper) are embedded, in
small batches so a mid-run failure doesn't lose already-computed vectors.

Keyed on (child_id, provider, model): switching embedding models must not
mix incompatible vectors of different dimensions, so a model change simply
means every chunk looks "missing" for that model and gets embedded fresh —
same invalidation behavior the old in-memory cache already had.
"""

import logging
import sqlite3
from pathlib import Path

import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)

EMBEDDING_DB_PATH = (Path(__file__).parent / "store" / "embeddings.sqlite").resolve()

# Small enough that one failed batch loses little progress and stays well
# under whatever caused the single 14,630-chunk request to fail; large
# enough that the per-request overhead doesn't dominate. At the ~17
# chunks/sec measured rate this is a few seconds per batch.
EMBED_BATCH_SIZE = 200


def _connect() -> sqlite3.Connection:
    EMBEDDING_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(EMBEDDING_DB_PATH), timeout=30)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS child_embeddings (
            child_id TEXT NOT NULL,
            paper_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            embedding BLOB NOT NULL,
            PRIMARY KEY (child_id, provider, model)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_child_embeddings_model ON child_embeddings(provider, model)"
    )
    return conn


def _vector_to_blob(vector: list[float]) -> bytes:
    return np.asarray(vector, dtype=np.float32).tobytes()


def _blob_to_vector(blob: bytes) -> list[float]:
    return np.frombuffer(blob, dtype=np.float32).tolist()


def _load_cached(conn: sqlite3.Connection, provider: str, model: str, child_ids: list[str]) -> dict[str, list[float]]:
    """Reads whichever of `child_ids` are already embedded for this
    provider/model. SQLite's default variable limit (999) means a single
    `IN (...)` can't hold thousands of ids, so this goes through the whole
    table for this model instead — one sequential scan, still fast at this
    row count (tens of thousands at most).
    """
    wanted = set(child_ids)
    found: dict[str, list[float]] = {}

    rows = conn.execute(
        "SELECT child_id, embedding FROM child_embeddings WHERE provider = ? AND model = ?",
        (provider, model),
    )

    for child_id, blob in rows:
        if child_id in wanted:
            found[child_id] = _blob_to_vector(blob)

    return found


def _store_batch(
    conn: sqlite3.Connection,
    provider: str,
    model: str,
    rows: list[tuple[str, str, list[float]]],
) -> None:
    conn.executemany(
        "INSERT OR REPLACE INTO child_embeddings (child_id, paper_id, provider, model, embedding) "
        "VALUES (?, ?, ?, ?, ?)",
        [(child_id, paper_id, provider, model, _vector_to_blob(vector)) for child_id, paper_id, vector in rows],
    )
    conn.commit()


def get_embeddings_for_documents(
    documents: list[Document], provider: str, model: str, embedder: Embeddings
) -> dict[str, list[float]]:
    """Returns {child_id: embedding_vector} for every document, computing
    and persisting only the ones not already cached for this provider/model.
    """

    conn = _connect()

    try:
        child_ids = [doc.metadata["child_id"] for doc in documents]
        cached = _load_cached(conn, provider, model, child_ids)

        missing = [doc for doc in documents if doc.metadata["child_id"] not in cached]

        if not missing:
            return cached

        logger.info(
            "Embedding %d new child chunk(s) for %s:%s (%d already cached)",
            len(missing), provider, model, len(cached),
        )

        for start in range(0, len(missing), EMBED_BATCH_SIZE):
            batch = missing[start : start + EMBED_BATCH_SIZE]
            vectors = embedder.embed_documents([doc.page_content for doc in batch])

            rows = [
                (doc.metadata["child_id"], doc.metadata["paper_id"], vector)
                for doc, vector in zip(batch, vectors)
            ]
            _store_batch(conn, provider, model, rows)

            for doc, vector in zip(batch, vectors):
                cached[doc.metadata["child_id"]] = vector

        return cached
    finally:
        conn.close()
