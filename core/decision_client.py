"""Client for Ollama's decision-model endpoint (/v1/systemone), shared by everything that uses `nimble`.

A decision model reads a `state` (named text fields) and answers CLOSED questions — pick an option,
yes/no with a probability — and never generates text. Requires Ollama 0.35 or later and
`ollama pull nimble`. Every use is optional: when the model is not installed or Ollama can't serve it,
`ask` raises `NimbleUnavailable`, callers treat that as "feature off", and the whole client backs off
for a few minutes so a missing model costs one failed request, not one per message.

Two limits shaped how it is used (see SECURITY_IMPLEMENTATION_PLAN.md, steps 5.7 and 5.8):
  * the prompt (state + questions) has to fit in 8,192 tokens, so only short texts go in;
  * it is 9.5 GB. On a small GPU loading it evicts the chat model, so it is only ever called AFTER a
    turn has finished, never inside the agent loop.
"""
import json
import logging
import os
import time
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

NIMBLE_MODEL = "nimble"
REQUEST_TIMEOUT_S = 90
BACKOFF_AFTER_FAILURE_S = 300

_disabled_until = 0.0


class NimbleUnavailable(Exception):
    """The decision model can't be reached (not installed, Ollama down, too old)."""


def base_url() -> str:
    host = os.environ.get("OLLAMA_HOST", "").strip() or "127.0.0.1:11434"
    if "://" not in host:
        host = "http://" + host
    return host.rstrip("/").replace("://0.0.0.0", "://127.0.0.1")


def backing_off() -> bool:
    return time.time() < _disabled_until


def back_off(reason: str) -> None:
    global _disabled_until
    _disabled_until = time.time() + BACKOFF_AFTER_FAILURE_S
    logger.info("Decision-model features off for %ss: %s", BACKOFF_AFTER_FAILURE_S, reason)


def reset_backoff() -> None:
    global _disabled_until
    _disabled_until = 0.0


def ask(state: dict, questions: dict) -> dict:
    """One /v1/systemone request; returns the `answers` block. Raises NimbleUnavailable on any transport
    problem. Malformed answers are the caller's to handle (they come back as whatever the server sent)."""
    body = json.dumps({"model": NIMBLE_MODEL, "state": state, "questions": questions}).encode()
    req = urllib.request.Request(base_url() + "/v1/systemone", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as r:
            return json.load(r)["answers"]
    except urllib.error.HTTPError as e:
        raise NimbleUnavailable(f"HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError) as e:
        raise NimbleUnavailable(type(e).__name__) from e
