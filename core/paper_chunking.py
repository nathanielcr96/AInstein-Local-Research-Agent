import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Parent/child hierarchical chunking for RAG over full paper content
# (distinct from search_memory, which only indexes paper abstracts).
# Small child chunks are what gets embedded and searched — precise, but
# too narrow to read on their own; each child's parent chunk is what
# actually gets returned to the model, wide enough to carry real context.
# Sizes are in tokens (cl100k_base, via tiktoken), not characters, so they
# stay meaningful across differently-verbose text.
PARENT_CHUNK_TOKENS = 1200
CHILD_CHUNK_TOKENS = 350
PARENT_CHUNK_OVERLAP_TOKENS = 150
CHILD_CHUNK_OVERLAP_TOKENS = 50

# core/paper_chunking.py -> parent is core/, parent.parent is the project
# root, where papers/ lives. child/ and parent/ sit alongside raw/ (see
# core/arxiv_download.py) as their own top-level stage, not nested under
# it, so each tier of the pipeline (raw text, parent chunks, child chunks)
# is a peer folder — mirrors how the project's own Goal describes storing
# external documents "through their proper stages".
PARENT_DIR = (Path(__file__).parent.parent / "papers" / "parent").resolve()
CHILD_DIR = (Path(__file__).parent.parent / "papers" / "child").resolve()


def _parent_path(paper_id: str) -> Path:
    return PARENT_DIR / f"{paper_id}.jsonl"


def _child_path(paper_id: str) -> Path:
    return CHILD_DIR / f"{paper_id}.jsonl"


def ensure_paper_chunks(paper_id: str, text: str) -> None:
    """
    Splits a paper's full text into parent/child chunks and writes them to
    papers/parent/<paper_id>.jsonl and papers/child/<paper_id>.jsonl (one
    chunk per line each) — unless both files already exist, in which case
    this is a no-op. Called every time download_paper succeeds (including
    from its own cache-hit path), so re-downloading an already-chunked
    paper never redoes the work.
    """

    parent_path = _parent_path(paper_id)
    child_path = _child_path(paper_id)

    if parent_path.exists() and child_path.exists():
        return

    PARENT_DIR.mkdir(parents=True, exist_ok=True)
    CHILD_DIR.mkdir(parents=True, exist_ok=True)

    parent_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=PARENT_CHUNK_TOKENS,
        chunk_overlap=PARENT_CHUNK_OVERLAP_TOKENS
    )
    child_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=CHILD_CHUNK_TOKENS,
        chunk_overlap=CHILD_CHUNK_OVERLAP_TOKENS
    )

    parent_records = []
    child_records = []

    for parent_index, parent_text in enumerate(parent_splitter.split_text(text)):

        parent_id = f"{paper_id}_p{parent_index}"

        parent_records.append({
            "parent_id": parent_id,
            "paper_id": paper_id,
            "index": parent_index,
            "text": parent_text
        })

        for child_index, child_text in enumerate(child_splitter.split_text(parent_text)):
            child_records.append({
                "child_id": f"{parent_id}_c{child_index}",
                "parent_id": parent_id,
                "paper_id": paper_id,
                "index": child_index,
                "text": child_text
            })

    with parent_path.open("w", encoding="utf-8") as f:
        for record in parent_records:
            f.write(json.dumps(record) + "\n")

    with child_path.open("w", encoding="utf-8") as f:
        for record in child_records:
            f.write(json.dumps(record) + "\n")
