import json
import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain.tools import tool

from memory.embedding_cache import get_embeddings_for_documents
from memory.memory_rag import _get_embeddings, _get_reranker, _rerank, RERANK_FETCH_K
from memory.memory_tools import _find_paper_entry, _parse_kv_block

logger = logging.getLogger(__name__)

# Reads what core/paper_chunking.py writes — this module never chunks
# anything itself, only searches and reassembles what's already there.
CHILD_DIR = (Path(__file__).parent.parent / "papers" / "child").resolve()
PARENT_DIR = (Path(__file__).parent.parent / "papers" / "parent").resolve()

# Same rebuild-in-memory philosophy as memory_rag.py's _load_index: the
# child-chunk FAISS index is a derived cache, never the source of truth
# (that's papers/child/*.jsonl itself). Rebuilt whenever the set of child
# files or their mtimes changes, or the embedding model changes.
_index_cache: dict = {"signature": None, "provider": None, "model": None, "store": None}


def _dir_signature(directory: Path) -> tuple:
    if not directory.exists():
        return ()
    return tuple(sorted((f.name, f.stat().st_mtime) for f in directory.glob("*.jsonl")))


def _load_child_documents() -> list[Document]:
    documents = []

    for file in sorted(CHILD_DIR.glob("*.jsonl")):
        for line in file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            documents.append(Document(
                page_content=record["text"],
                metadata={
                    "child_id": record["child_id"],
                    "parent_id": record["parent_id"],
                    "paper_id": record["paper_id"]
                }
            ))

    return documents


def _load_index(provider: str, model: str) -> FAISS | None:
    signature = _dir_signature(CHILD_DIR)

    cache_hit = (
        _index_cache["store"] is not None
        and _index_cache["signature"] == signature
        and _index_cache["provider"] == provider
        and _index_cache["model"] == model
    )

    if cache_hit:
        return _index_cache["store"]

    documents = _load_child_documents()

    if not documents:
        return None

    embeddings = _get_embeddings(provider, model)

    # The actual embedding vectors are read from (and, for any new chunk,
    # written to) memory/store/embeddings.sqlite — see embedding_cache.py
    # for why: embedding all ~14,600 child chunks in one request on every
    # cold start was verified live to fail partway through. This call only
    # calls Ollama for chunks that aren't cached yet (a newly downloaded
    # paper); everything else comes back from SQLite in well under a
    # second. FAISS.from_embeddings builds the same in-memory search index
    # as FAISS.from_documents did, just skipping the embedding step for
    # chunks already on disk.
    vectors_by_child_id = get_embeddings_for_documents(documents, provider, model, embeddings)

    text_embeddings = [
        (doc.page_content, vectors_by_child_id[doc.metadata["child_id"]]) for doc in documents
    ]
    metadatas = [doc.metadata for doc in documents]

    store = FAISS.from_embeddings(text_embeddings, embeddings, metadatas=metadatas)

    _index_cache.update(signature=signature, provider=provider, model=model, store=store)

    return store


def _load_parent_text(paper_id: str, parent_id: str) -> str | None:
    parent_path = PARENT_DIR / f"{paper_id}.jsonl"

    if not parent_path.exists():
        return None

    for line in parent_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record["parent_id"] == parent_id:
            return record["text"]

    return None


def _paper_header(paper_id: str) -> str:
    """
    Short citation header (arXiv id / title / authors) prepended to every
    passage returned to the model. Reuses the exact metadata
    PaperMemoryMiddleware already saves to long-term memory for this paper
    — deliberately not stored a second time here.
    """

    entry = _find_paper_entry(paper_id)

    if entry is None:
        return f"arXiv ID: {paper_id}"

    fields = _parse_kv_block(entry["content"])

    parts = [f"arXiv ID: {paper_id}"]

    if fields.get("Title"):
        parts.append(f"Title: {fields['Title']}")

    if fields.get("Authors"):
        parts.append(f"Authors: {fields['Authors']}")

    return "\n".join(parts)


def make_search_paper_content_tool(provider: str, model: str):
    """
    Builds the `search_paper_content` tool bound to a specific embedding
    provider/model — same reasoning as `make_search_memory_tool`: the
    embedding model is chosen per session, not fixed for the whole app.
    """

    @tool
    def search_paper_content(query: str, paper_id: str | None = None, k: int = 5) -> str:
        """
        Searches the full text of already-downloaded papers for passages
        relevant to `query` — unlike `search_memory`, which only covers
        abstracts and notes, this searches the actual paper content saved
        by `download_paper`.

        Pass `paper_id` to restrict the search to one specific paper;
        omit it to search across every downloaded paper. Returns at most
        `k` passages (5 by default), each prefixed with the paper's
        title/authors/arXiv id so it can be cited properly.
        """

        k = max(1, min(k, 20))

        try:
            store = _load_index(provider, model)
        except Exception as exc:
            return f"Error generating embeddings with '{provider}:{model}': {exc}"

        if store is None:
            return "No downloaded papers have been indexed for content search yet."

        fetch_k = max(RERANK_FETCH_K, k) * (3 if paper_id else 1)
        candidates = store.similarity_search(query, k=fetch_k)

        if paper_id:
            candidates = [doc for doc in candidates if doc.metadata["paper_id"] == paper_id]

        try:
            results = _rerank(query, candidates, k)
        except Exception:
            logger.exception("Reranker failed, returning unreordered FAISS order")
            results = candidates[:k]

        if not results:
            return "No relevant passage was found."

        # A paper's neighboring child chunks often share the same parent —
        # only emit each parent block once, in rerank-score order.
        parent_blocks: dict[str, str] = {}

        for doc in results:
            parent_id = doc.metadata["parent_id"]

            if parent_id in parent_blocks:
                continue

            paper_id_ = doc.metadata["paper_id"]
            parent_text = _load_parent_text(paper_id_, parent_id) or doc.page_content
            header = _paper_header(paper_id_)

            parent_blocks[parent_id] = f"{header}\n\n{parent_text}"

        return "\n\n---\n\n".join(parent_blocks.values())

    return search_paper_content
