import logging

from huggingface_hub import scan_cache_dir

logger = logging.getLogger(__name__)

def _latest_revision(repo):
    """The most recent revision of a cached repo (by last_modified)."""

    revisions = list(repo.revisions)

    if not revisions:
        return None

    return max(revisions, key=lambda rev: rev.last_modified)

def _is_sentence_transformers_model(repo) -> bool:
    """
    `modules.json` is the standard marker of a sentence-transformers
    compatible model (what HuggingFaceEmbeddings uses) — its presence is
    the usual way to tell an embedding model apart from any other model
    (chat, vision, layout, etc.) without having to download or run it.
    """

    revision = _latest_revision(repo)

    if revision is None:
        return False

    return any(f.file_name == "modules.json" for f in revision.files)

def get_huggingface_models_info() -> dict:
    """
    Catalogs the models present in the local HuggingFace cache (usually
    ~/.cache/huggingface/hub).

    This is just a disk inventory: it doesn't run anything. `is_embedding`
    distinguishes sentence-transformers compatible models (see
    `_is_sentence_transformers_model`) from the rest — the rest could be
    chat, vision, layout, etc. models, and none of them have execution
    implemented yet in this agent.
    """

    try:

        cache_info = scan_cache_dir()

    except Exception:

        logger.exception("Could not scan the local HuggingFace cache")

        return {}

    models = {}

    for repo in cache_info.repos:

        if repo.repo_type != "model":
            continue

        models[repo.repo_id] = {
            "size_on_disk": repo.size_on_disk,
            "size_on_disk_human": repo.size_on_disk_str,
            "last_modified": repo.last_modified_str,
            "path": str(repo.repo_path),
            "is_embedding": _is_sentence_transformers_model(repo)
        }

    return models
