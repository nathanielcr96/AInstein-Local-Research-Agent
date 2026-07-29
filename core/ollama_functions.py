import time

import ollama

_MODELS_CACHE_TTL_SECONDS = 60
_models_cache: dict = {"data": None, "fetched_at": 0.0}

def _extract_context_length(model_info: dict) -> int:
    """
    model_info carries context_length under a key prefixed with the
    model's architecture (e.g. "llama.context_length",
    "qwen35.context_length", "bert.context_length") — there's no single
    fixed key common to all of them.
    """

    architecture = model_info.get("general.architecture")

    if architecture:

        key = f"{architecture}.context_length"

        if key in model_info:
            return model_info[key]

    for key, value in model_info.items():

        if key.endswith(".context_length"):
            return value

    return 8192

def get_ollama_models_info(force_refresh: bool = False) -> dict:
    """
    Lists installed Ollama models along with their context_length and
    capabilities (e.g. "completion", "tools", "embedding") — the latter
    lets us tell chat models apart from embedding models.

    Uses the `ollama` python client (local REST API), not the CLI: the CLI
    changes syntax between versions (e.g. the `--json` flag of
    `ollama show` disappeared in 0.31.2 without warning, and
    `subprocess` + text-parsing `ollama list` is just as fragile against
    format changes).

    Cached in memory for _MODELS_CACHE_TTL_SECONDS: without this, every
    call fires a query per installed model, and this helper is called on
    every chat message, not just at startup.
    """

    now = time.time()

    if (
        not force_refresh
        and _models_cache["data"] is not None
        and (now - _models_cache["fetched_at"]) < _MODELS_CACHE_TTL_SECONDS
    ):
        return _models_cache["data"]

    models = {}

    try:
        listing = ollama.list()
    except Exception:
        listing = None

    for entry in (listing.models if listing else []):

        model_name = entry.model

        try:

            details = ollama.show(model_name)

            capabilities = list(details.capabilities or [])

            context_length = _extract_context_length(details.modelinfo or {})

        except Exception:

            capabilities = []

            context_length = 8192

        models[model_name] = {
            "context_length": context_length,
            "capabilities": capabilities,
            "is_chat": "completion" in capabilities,
            "is_embedding": "embedding" in capabilities
        }

    _models_cache["data"] = models
    _models_cache["fetched_at"] = now

    return models

def extract_llm_metrics(event):

    output = event["data"]["output"]

    usage = getattr(output, "usage_metadata", None) or {}

    metadata = getattr(output, "response_metadata", None) or {}

    return {
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "duration": metadata.get("total_duration", 0) / 1_000_000_000
    }
