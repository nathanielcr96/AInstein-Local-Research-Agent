import logging

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from langchain.tools import tool

from memory.memory_tools import MEMORY_FILE, _list_memory_entries

logger = logging.getLogger(__name__)

# Two-stage reranker: FAISS fetches RERANK_FETCH_K cheap candidates by
# approximate similarity, a cross-encoder scores them one by one with
# precision, and only then do we keep the top k. Embedding similarity
# alone didn't rank well on small corpora (verified: a clearly relevant
# paper came out 3rd of 4). ms-marco-MiniLM-L6-v2 instead of something
# multilingual because the most important content going forward (papers)
# will be in English, not Spanish — it's the de facto standard for
# English reranking: small (~90MB), fast on CPU, Apache 2.0.
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L6-v2"
RERANK_FETCH_K = 15

_reranker_cache: dict = {"model": None}

def _get_reranker():

    if _reranker_cache["model"] is None:

        from langchain_community.cross_encoders import HuggingFaceCrossEncoder

        _reranker_cache["model"] = HuggingFaceCrossEncoder(model_name=RERANKER_MODEL_NAME)

    return _reranker_cache["model"]

def _rerank(query: str, documents: list[Document], k: int) -> list[Document]:

    if not documents:
        return []

    reranker = _get_reranker()

    pairs = [(query, doc.page_content) for doc in documents]

    scores = reranker.score(pairs)

    ranked = sorted(zip(documents, scores), key=lambda pair: pair[1], reverse=True)

    return [doc for doc, _score in ranked[:k]]

# The FAISS index is a derived cache, never the source of truth — that
# remains memory/store/long_term.md. It's rebuilt entirely in memory
# whenever the file changes (by mtime) or the chosen embedding model
# changes; it isn't persisted to disk. Given the expected volume of
# entries (tens/hundreds, not thousands), rebuilding is cheap and avoids
# all the complexity of keeping a persistent index in sync with
# update_memory/edit_memory.
_index_cache: dict = {"mtime": None, "provider": None, "model": None, "store": None}

def _get_embeddings(provider: str, model: str) -> Embeddings:

    if provider == "ollama":

        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(model=model)

    if provider == "huggingface":

        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError as exc:
            raise RuntimeError(
                "Using a HuggingFace embedding model requires installing "
                "'langchain-huggingface' and 'sentence-transformers' "
                "(pip install langchain-huggingface sentence-transformers)."
            ) from exc

        return HuggingFaceEmbeddings(model_name=model)

    raise ValueError(f"Unknown embedding provider: '{provider}'.")

def _load_index(provider: str, model: str) -> FAISS | None:

    mtime = MEMORY_FILE.stat().st_mtime if MEMORY_FILE.exists() else None

    cache_hit = (
        _index_cache["store"] is not None
        and _index_cache["mtime"] == mtime
        and _index_cache["provider"] == provider
        and _index_cache["model"] == model
    )

    if cache_hit:
        return _index_cache["store"]

    if not MEMORY_FILE.exists():
        return None

    entries = _list_memory_entries(MEMORY_FILE.read_text(encoding="utf-8"))

    if not entries:
        return None

    docs = [
        Document(
            page_content=entry["content"],
            metadata={
                "id": entry["id"],
                "category": entry["category"],
                "timestamp": entry["timestamp"]
            }
        )
        for entry in entries
    ]

    embeddings = _get_embeddings(provider, model)

    store = FAISS.from_documents(docs, embeddings)

    _index_cache.update(
        mtime=mtime,
        provider=provider,
        model=model,
        store=store
    )

    return store

def make_search_memory_tool(provider: str, model: str):
    """
    Builds the `search_memory` tool bound to a specific embedding
    provider/model — needed because the embedding model is chosen per
    session (in the chat settings), not fixed for the whole app.
    """

    @tool
    def search_memory(query: str, k: int = 5) -> str:
        """
        Searches long-term memory for the entries most relevant to
        `query`, by semantic similarity (not a literal text search).

        Returns at most `k` entries (5 by default), from most to least
        relevant — retrieved by similarity and reranked by a reranker
        for greater precision. Call this before answering when the
        conversation topic might relate to something already saved:
        active research, user preferences, previous papers, etc.
        """

        k = max(1, min(k, 20))

        try:
            store = _load_index(provider, model)
        except Exception as exc:
            return f"Error generating embeddings with '{provider}:{model}': {exc}"

        if store is None:
            return "Long-term memory is still empty."

        candidates = store.similarity_search(query, k=max(k, RERANK_FETCH_K))

        try:
            results = _rerank(query, candidates, k)
        except Exception:
            logger.exception("Reranker failed, returning unreordered FAISS order")
            results = candidates[:k]

        if not results:
            return "No relevant entry was found in memory."

        return "\n\n---\n\n".join(
            f"[{r.metadata['id']}] {r.metadata['category']} — {r.metadata['timestamp']}\n{r.page_content}"
            for r in results
        )

    return search_memory
