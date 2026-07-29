from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any

from langchain.agents.middleware.types import AgentMiddleware, ExtendedModelResponse, ModelResponse
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from langchain_ollama import ChatOllama

from prompts.ensure_final_answer_prompt import (
    NUDGE_MESSAGE,
    FALLBACK_MESSAGE,
    FALLBACK_MODEL_UNAVAILABLE_MESSAGE,
)
from memory.memory_tools import MEMORY_FILE, _list_memory_entries, update_memory, edit_memory

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from langchain.agents.middleware.types import ModelRequest, ResponseT, ToolCallRequest
    from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


def _tool_name(tool: "BaseTool | dict[str, Any]") -> str | None:
    if isinstance(tool, dict):
        name = tool.get("name")
        return name if isinstance(name, str) else None
    return getattr(tool, "name", None)


class ExcludeToolsMiddleware(AgentMiddleware[Any, Any, Any]):
    """Hides tools by name from the model's tool list.

    The tools are still registered in the graph (other middleware can still
    call them internally), they just never appear in what the model sees,
    so the model can't invoke them itself.
    """

    def __init__(self, *, excluded: set[str]) -> None:
        self._excluded = frozenset(excluded)

    def wrap_model_call(
        self,
        request: "ModelRequest[Any]",
        handler: "Callable[[ModelRequest[Any]], ModelResponse[Any]]",
    ) -> "ModelResponse[Any]":
        if self._excluded:
            request = request.override(tools=[t for t in request.tools if _tool_name(t) not in self._excluded])
        return handler(request)

    async def awrap_model_call(
        self,
        request: "ModelRequest[Any]",
        handler: "Callable[[ModelRequest[Any]], Awaitable[ModelResponse[ResponseT]]]",
    ) -> "ModelResponse[ResponseT] | AIMessage":
        if self._excluded:
            request = request.override(tools=[t for t in request.tools if _tool_name(t) not in self._excluded])
        return await handler(request)


def _final_ai_message(response: Any) -> AIMessage | None:
    if isinstance(response, AIMessage):
        return response
    if isinstance(response, ExtendedModelResponse):
        response = response.model_response
    if isinstance(response, ModelResponse):
        for msg in reversed(response.result):
            if isinstance(msg, AIMessage):
                return msg
    return None


def _is_empty_final(ai_message: AIMessage | None) -> bool:
    if ai_message is None or ai_message.tool_calls:
        return False
    content = ai_message.text if hasattr(ai_message, "text") else str(ai_message.content or "")
    return not content.strip()


def _replace_ai_content(response: Any, text: str) -> Any:
    if isinstance(response, AIMessage):
        return response.model_copy(update={"content": text})
    if isinstance(response, ExtendedModelResponse):
        response.model_response = _replace_ai_content(response.model_response, text)
        return response
    if isinstance(response, ModelResponse):
        new_result = list(response.result)
        for i in range(len(new_result) - 1, -1, -1):
            if isinstance(new_result[i], AIMessage):
                new_result[i] = new_result[i].model_copy(update={"content": text})
                break
        response.result = new_result
        return response
    return response


# Hardcoded rather than user-configurable: this is a last-resort safety
# net, not a normal model choice, so it doesn't need its own chat-settings
# dropdown. llama3.2:3b was picked because it's the small model this
# project was actually tested against (see README "Tested with").
_FALLBACK_MODEL_NAME = "llama3.2:3b"

_fallback_model_cache: dict = {"model": None}

def _get_fallback_model() -> ChatOllama:
    if _fallback_model_cache["model"] is None:
        # temperature=0: this tier only runs when the selected model has
        # already failed to produce a final answer twice, so the goal is
        # a plain, reliable response, not variety.
        _fallback_model_cache["model"] = ChatOllama(model=_FALLBACK_MODEL_NAME, temperature=0)
    return _fallback_model_cache["model"]


class EnsureFinalAnswerMiddleware(AgentMiddleware[Any, Any, Any]):
    """Guarantees the turn never ends on an empty, non-tool-call response.

    Some small local models stop right after a tool result with an empty
    AIMessage and no further tool calls — the graph treats that as "done",
    leaving the user with a blank reply. Instead of hoping the model
    voluntarily follows a prompt instruction (a skill, a system prompt line),
    this re-asks the model directly up to `max_retries` times.

    If the originally selected model still won't answer, there's a second
    tier before giving up: the same number of retries again, but against a
    small fixed fallback model (`_FALLBACK_MODEL_NAME`) instead of the one
    the user picked — cheap insurance against the selected model being the
    specific thing struggling with this turn. Only if that also fails (or
    the fallback model isn't even available, e.g. not pulled in Ollama) does
    this fall back to a fixed, honest message so the conversation never ends
    in blank.
    """

    def __init__(self, *, max_retries: int = 2) -> None:
        self._max_retries = max_retries

    def wrap_model_call(
        self,
        request: "ModelRequest[Any]",
        handler: "Callable[[ModelRequest[Any]], ModelResponse[Any]]",
    ) -> "ModelResponse[Any]":
        current_request = request
        response = handler(current_request)
        attempts = 0

        while _is_empty_final(_final_ai_message(response)) and attempts < self._max_retries:
            attempts += 1
            current_request = current_request.override(
                messages=[*current_request.messages, HumanMessage(content=NUDGE_MESSAGE)]
            )
            response = handler(current_request)

        if not _is_empty_final(_final_ai_message(response)):
            return response

        try:
            fallback_request = current_request.override(model=_get_fallback_model())
            response = handler(fallback_request)
            attempts = 0

            while _is_empty_final(_final_ai_message(response)) and attempts < self._max_retries:
                attempts += 1
                fallback_request = fallback_request.override(
                    messages=[*fallback_request.messages, HumanMessage(content=NUDGE_MESSAGE)]
                )
                response = handler(fallback_request)
        except Exception:
            logger.exception("Fallback model '%s' could not be called", _FALLBACK_MODEL_NAME)
            return _replace_ai_content(
                response, FALLBACK_MODEL_UNAVAILABLE_MESSAGE.format(model=_FALLBACK_MODEL_NAME)
            )

        if _is_empty_final(_final_ai_message(response)):
            response = _replace_ai_content(response, FALLBACK_MESSAGE)

        return response

    async def awrap_model_call(
        self,
        request: "ModelRequest[Any]",
        handler: "Callable[[ModelRequest[Any]], Awaitable[ModelResponse[ResponseT]]]",
    ) -> "ModelResponse[ResponseT] | AIMessage":
        current_request = request
        response = await handler(current_request)
        attempts = 0

        while _is_empty_final(_final_ai_message(response)) and attempts < self._max_retries:
            attempts += 1
            current_request = current_request.override(
                messages=[*current_request.messages, HumanMessage(content=NUDGE_MESSAGE)]
            )
            response = await handler(current_request)

        if not _is_empty_final(_final_ai_message(response)):
            return response

        try:
            fallback_request = current_request.override(model=_get_fallback_model())
            response = await handler(fallback_request)
            attempts = 0

            while _is_empty_final(_final_ai_message(response)) and attempts < self._max_retries:
                attempts += 1
                fallback_request = fallback_request.override(
                    messages=[*fallback_request.messages, HumanMessage(content=NUDGE_MESSAGE)]
                )
                response = await handler(fallback_request)
        except Exception:
            logger.exception("Fallback model '%s' could not be called", _FALLBACK_MODEL_NAME)
            return _replace_ai_content(
                response, FALLBACK_MODEL_UNAVAILABLE_MESSAGE.format(model=_FALLBACK_MODEL_NAME)
            )

        if _is_empty_final(_final_ai_message(response)):
            response = _replace_ai_content(response, FALLBACK_MESSAGE)

        return response


_TRACKED_ARXIV_TOOLS = {"get_abstract", "download_paper", "read_paper"}

# Field order used when serializing a "paper" memory entry as a flat
# key: value block, one field per line (kept single-line, including
# Abstract, so the block can be parsed back with a plain split on the
# first ":" per line).
_PAPER_FIELD_ORDER = ["arXiv ID", "Title", "Authors", "Categories", "Published", "Local file", "Abstract"]


def _tool_message_text(result: Any) -> str | None:
    if not isinstance(result, ToolMessage):
        return None
    content = result.content
    if isinstance(content, list):
        parts = [block.get("text", "") if isinstance(block, dict) else str(block) for block in content]
        return "\n".join(parts)
    return str(content) if content is not None else None


def _parse_kv_block(content: str) -> dict[str, str]:
    fields = {}
    for line in content.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key:
            fields[key] = value.strip()
    return fields


def _format_kv_block(fields: dict[str, str]) -> str:
    ordered = [f"{key}: {fields[key]}" for key in _PAPER_FIELD_ORDER if fields.get(key)]
    extra = [f"{key}: {fields[key]}" for key in fields if key not in _PAPER_FIELD_ORDER and fields.get(key)]
    return "\n".join(ordered + extra)


def _find_paper_entry(paper_id: str) -> dict | None:
    if not MEMORY_FILE.exists():
        return None
    text = MEMORY_FILE.read_text(encoding="utf-8")
    marker = f"arXiv ID: {paper_id}"
    for entry in _list_memory_entries(text):
        if entry["category"] == "paper" and marker in entry["content"]:
            return entry
    return None


class PaperMemoryMiddleware(AgentMiddleware[Any, Any, Any]):
    """Auto-saves every arXiv paper the agent inspects into long-term memory.

    A small local model can't be relied on to remember, on its own, to call
    `update_memory` after reading a paper — verified empirically: across two
    full research conversations it never called it once. Instead of hoping
    the model follows a prompt instruction, this deterministically writes a
    baseline entry (arXiv id, title, authors, abstract, local file path)
    every time `get_abstract`, `download_paper`, or `read_paper` succeeds,
    regardless of what the model decides to do next.

    Fields accumulate across calls for the same paper_id (e.g. `get_abstract`
    contributes title/authors/abstract, a later `download_paper` adds the
    local file path) by merging into the existing entry via `edit_memory`
    instead of creating a duplicate. The model can still enrich the entry
    further with its own synthesis of key findings via `edit_memory`.
    """

    def wrap_tool_call(
        self,
        request: "ToolCallRequest",
        handler: "Callable[[ToolCallRequest], ToolMessage | Any]",
    ) -> "ToolMessage | Any":
        result = handler(request)
        self._maybe_record_paper(request, result)
        return result

    async def awrap_tool_call(
        self,
        request: "ToolCallRequest",
        handler: "Callable[[ToolCallRequest], Awaitable[ToolMessage | Any]]",
    ) -> "ToolMessage | Any":
        result = await handler(request)
        self._maybe_record_paper(request, result)
        return result

    def _maybe_record_paper(self, request: "ToolCallRequest", result: Any) -> None:
        tool_name = request.tool_call.get("name")

        if tool_name not in _TRACKED_ARXIV_TOOLS:
            return

        try:
            self._record_paper(tool_name, request.tool_call.get("args") or {}, result)
        except Exception:
            logger.exception("Failed to auto-save paper to long-term memory")

    def _record_paper(self, tool_name: str, args: dict, result: Any) -> None:
        text = _tool_message_text(result)

        if not text:
            return

        try:
            payload = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return

        if payload.get("status") != "success":
            return

        paper_id = payload.get("paper_id") or args.get("paper_id")

        if not paper_id:
            return

        new_fields = {"arXiv ID": paper_id}

        if tool_name == "get_abstract":
            new_fields["Title"] = payload.get("title", "")
            new_fields["Authors"] = ", ".join(payload.get("authors") or [])
            new_fields["Categories"] = ", ".join(payload.get("categories") or [])
            new_fields["Published"] = payload.get("published", "")
            new_fields["Abstract"] = (payload.get("abstract") or "").replace("\n", " ").strip()
        else:
            new_fields["Local file"] = f"papers/{paper_id}.md (full text retrieved)"

        existing = _find_paper_entry(paper_id)

        if existing is None:
            content = _format_kv_block(new_fields)
            if content:
                update_memory.func(content=content, category="paper")
            return

        merged = _parse_kv_block(existing["content"])
        merged.update({key: value for key, value in new_fields.items() if value})
        edit_memory.func(entry_id=existing["id"], content=_format_kv_block(merged), category="paper")


_ARXIV_TOOL_NAMES = {
    "search_papers", "get_abstract", "download_paper", "read_paper",
    "list_papers", "semantic_search", "reindex", "citation_graph",
    "watch_topic", "check_alerts"
}

_ARXIV_TOOL_TIMEOUT_SECONDS = 90


class ArxivTimeoutMiddleware(AgentMiddleware[Any, Any, Any]):
    """Bounds how long an arXiv MCP tool call can run before giving up.

    Verified directly against the live arxiv-mcp-server: when arXiv's own
    search/metadata endpoint (export.arxiv.org, used to resolve a paper's
    PDF URL before downloading it) starts rate-limiting a client with
    HTTP 429, the underlying `arxiv` package retries with growing backoff
    and doesn't raise for a long time — from here, that reads as the tool
    call simply never returning, which previously left the whole turn
    stuck indefinitely with no feedback. Cutting it off after
    `_ARXIV_TOOL_TIMEOUT_SECONDS` turns that silent hang into a fast,
    legible error the model (and ARXIV_PROMPT's own guidance) can react
    to, instead of the user having to notice nothing is happening and
    manually stop/refresh.

    Deliberately no automatic retry here: arXiv's rate limiting is exactly
    what caused the hang, so retrying quickly would just add more requests
    into the same throttling window and risk making it worse.
    """

    async def awrap_tool_call(
        self,
        request: "ToolCallRequest",
        handler: "Callable[[ToolCallRequest], Awaitable[ToolMessage | Any]]",
    ) -> "ToolMessage | Any":
        tool_name = request.tool_call.get("name")

        if tool_name not in _ARXIV_TOOL_NAMES:
            return await handler(request)

        try:
            return await asyncio.wait_for(handler(request), timeout=_ARXIV_TOOL_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            logger.warning("arXiv tool '%s' timed out after %ss", tool_name, _ARXIV_TOOL_TIMEOUT_SECONDS)
            return ToolMessage(
                content=(
                    f"Error: {tool_name} did not respond within {_ARXIV_TOOL_TIMEOUT_SECONDS}s. "
                    "This usually means arXiv is rate-limiting requests right now, not that "
                    "anything is broken. Wait about a minute before trying again, and avoid "
                    "calling arXiv tools repeatedly in a tight loop in the meantime."
                ),
                tool_call_id=request.tool_call["id"],
                status="error"
            )
