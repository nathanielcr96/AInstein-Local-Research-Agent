from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import TYPE_CHECKING, Any

from langchain.agents.middleware.types import AgentMiddleware, ExtendedModelResponse, ModelResponse
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from langchain_ollama import ChatOllama
from ollama import ResponseError as OllamaResponseError

from prompts.ensure_final_answer_prompt import (
    NUDGE_MESSAGE,
    NUDGE_MESSAGE_TEMPLATE,
    FALLBACK_MESSAGE,
    FALLBACK_MODEL_UNAVAILABLE_MESSAGE,
)
from memory.memory_tools import (
    update_memory,
    edit_memory,
    _parse_kv_block,
    _format_kv_block,
    _find_paper_entry,
)
from core.tools import read_skill

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


_EXCLUDED_TOOL_CALL_MESSAGE = (
    "Error: '{name}' is not available in this agent — it was never offered to you as a "
    "tool, so this call was hallucinated rather than a real option. Do not call it again. "
    "Use one of the tools you actually have instead: `search_paper_content` or `read_paper` "
    "for a paper's content, `search_memory` for what's already saved, `read_skill` for a "
    "skill's instructions."
)


class ExcludeToolsMiddleware(AgentMiddleware[Any, Any, Any]):
    """Hides tools by name from the model's tool list, and rejects a call to
    one with a clear error instead of letting it reach the real tool.

    The tools are still registered in the graph (other middleware can still
    call them internally), they just never appear in what the model sees —
    but a name it was never shown isn't out of reach for a model to *call*
    anyway (verified live: `qwen3.5:4b` invoked `read_file`, one of these
    hidden tools, more than once despite it never being in its tool list,
    presumably pattern-matching to a common agentic-coding tool name from
    training rather than anything in this session's context). Filtering
    only the model-facing schema (`wrap_model_call` below) doesn't stop
    that — a `tool_calls` entry naming an excluded tool still reaches the
    real tool node. For most of `HIDDEN_TOOLS` that's caught by
    `deepagents`' own filesystem-interrupt safety net (verified directly:
    no file content actually leaked), but that path expects a human to
    resolve the interrupt — with no one there to do that, the turn can
    just hang instead of failing cleanly. `wrap_tool_call` intercepts a
    call to an excluded name before it gets that far, returning a plain
    tool-error message the model can act on immediately instead.
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

    def wrap_tool_call(
        self,
        request: "ToolCallRequest",
        handler: "Callable[[ToolCallRequest], ToolMessage | Any]",
    ) -> "ToolMessage | Any":
        name = request.tool_call.get("name")
        if name in self._excluded:
            return ToolMessage(
                content=_EXCLUDED_TOOL_CALL_MESSAGE.format(name=name),
                tool_call_id=request.tool_call["id"],
                status="error",
            )
        return handler(request)

    async def awrap_tool_call(
        self,
        request: "ToolCallRequest",
        handler: "Callable[[ToolCallRequest], Awaitable[ToolMessage | Any]]",
    ) -> "ToolMessage | Any":
        name = request.tool_call.get("name")
        if name in self._excluded:
            return ToolMessage(
                content=_EXCLUDED_TOOL_CALL_MESSAGE.format(name=name),
                tool_call_id=request.tool_call["id"],
                status="error",
            )
        return await handler(request)


_ANALYSIS_TRIGGER_RE = re.compile(r"\banalys|\banalyz", re.IGNORECASE)

_FORCED_SKILL_MARKER = "[auto-loaded: paper-analysis skill]"

_DEPTH_MODE_RE = re.compile(r"\b(quick|standard|extended)\b", re.IGNORECASE)


def _detect_depth_mode(text: str) -> str | None:
    """Finds a depth word ("quick"/"standard"/"extended") the user's own
    message already contains.

    Told to the model as an already-resolved directive rather than left for
    it to notice on its own: verified live that even an explicit skill rule
    ("if the user's message contains this word, use it directly") didn't
    reliably work — a message containing "extended analysis" was still
    answered in Quick mode's 5-point structure twice in a row. Computing it
    here and stating it as a fact ("DEPTH MODE: EXTENDED") removes the step
    that kept failing: the model no longer has to notice or apply the rule
    itself, only read an already-made decision.
    """
    match = _DEPTH_MODE_RE.search(text)
    return match.group(1).lower() if match else None


class ForcePaperAnalysisSkillMiddleware(AgentMiddleware[Any, Any, Any]):
    """Deterministically injects the `paper-analysis` skill's full
    instructions into context the moment the user's message contains
    "analysis"/"analyze" in any form, instead of relying on the model to
    decide to call `read_skill` for it itself.

    Verified live (point 9 of the memory-seeding test list): qwen3.5:4b
    failed to call `read_skill('paper-analysis')` on its own in 2/2 retests
    of a prompt that literally contained "extended analysis" — even after
    `CUSTOM_SKILLS_SYSTEM_PROMPT` was hardened with an explicit, blunt,
    keyword-specific rule naming this exact case. Same lesson already
    applied by `PaperMemoryMiddleware` (auto-saving papers instead of
    trusting `update_memory` to be called): for something this
    load-bearing, don't hope a small local model follows a prompt
    instruction — enforce it in code instead.

    Injected once per turn, not once per model call: the ReAct loop calls
    `wrap_model_call` repeatedly within a single turn as tool calls happen,
    and `_FORCED_SKILL_MARKER` already appearing after the triggering
    HumanMessage is what prevents re-injecting the full skill text (and
    wasting context) on every one of those after the first.
    """

    def wrap_model_call(
        self,
        request: "ModelRequest[Any]",
        handler: "Callable[[ModelRequest[Any]], ModelResponse[Any]]",
    ) -> "ModelResponse[Any]":
        return handler(self._maybe_inject(request))

    async def awrap_model_call(
        self,
        request: "ModelRequest[Any]",
        handler: "Callable[[ModelRequest[Any]], Awaitable[ModelResponse[ResponseT]]]",
    ) -> "ModelResponse[ResponseT] | AIMessage":
        return await handler(self._maybe_inject(request))

    def _maybe_inject(self, request: "ModelRequest[Any]") -> "ModelRequest[Any]":
        messages = request.messages

        last_human_idx = None
        for i in range(len(messages) - 1, -1, -1):
            if isinstance(messages[i], HumanMessage):
                last_human_idx = i
                break

        if last_human_idx is None:
            return request

        human_text = _message_text(messages[last_human_idx].content)

        if not _ANALYSIS_TRIGGER_RE.search(human_text):
            return request

        already_injected = any(
            isinstance(msg, SystemMessage) and _FORCED_SKILL_MARKER in _message_text(msg.content)
            for msg in messages[last_human_idx + 1 :]
        )

        if already_injected:
            return request

        skill_text = read_skill.func(skill_name="paper-analysis")

        if skill_text.startswith("Error:"):
            logger.warning("ForcePaperAnalysisSkillMiddleware: %s", skill_text)
            return request

        depth_mode = _detect_depth_mode(human_text)
        depth_line = (
            f"DEPTH MODE FOR THIS REQUEST: {depth_mode.upper()} — the user's own message "
            f"contains the word \"{depth_mode}\", so this is already decided, not something "
            f"to infer from context. Use the **{depth_mode.capitalize()}** section below and "
            "no other.\n\n"
            if depth_mode
            else ""
        )

        injected = SystemMessage(
            content=(
                f"{_FORCED_SKILL_MARKER} The user's message contains "
                "\"analysis\"/\"analyze\", so the paper-analysis skill's full "
                "instructions are loaded below automatically — you do not need "
                "to (and should not) call read_skill for it yourself. Follow "
                "these instructions for this turn:\n\n" + depth_line + skill_text
            )
        )

        new_messages = list(messages)
        new_messages.insert(last_human_idx + 1, injected)

        return request.override(messages=new_messages)


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


_TEXTUAL_TOOL_CALL_KEYS_NAME = ("tool_name", "tool_call", "tool_call_id", "name", "function")
_TEXTUAL_TOOL_CALL_KEYS_ARGS = ("args", "arguments", "parameters", "input")
# Keys that mark a JSON blob as a *described action / plan* rather than data —
# qwen3.5:4b has ended turns with e.g. {"task": "continue_reading_paper",
# "description": "..."} instead of actually calling the tool.
_TEXTUAL_ACTION_KEYS = ("task", "action", "next_step", "next_action", "step", "command", "plan")
# Prose that signals the model stalled mid-task ("...before I answer") rather
# than actually answering.
_STALL_PHRASE_RE = re.compile(
    r"\b("
    r"let me (continue|retrieve|read|get|fetch|check|look)"
    r"|continue reading"
    r"|i'?ll continue"
    r"|(retrieve|read|get|fetch) the (next|rest|remaining)"
    r"|next chunk"
    r"|before (providing|i provide|giving|i give|i can (provide|answer)|analysis)"
    r"|to get a complete (view|picture|understanding)"
    r")\b",
    re.IGNORECASE,
)


def _looks_like_textual_tool_call(content: str) -> bool:
    """True when the model *described* a tool call / next action in its text
    instead of actually emitting one, and gave no real answer — e.g. a
    ```json {"tool_name": ..., "args": ...}``` block or a
    {"task": "continue_reading_paper", ...} blob, usually prefaced with
    "let me retrieve the next chunk" / "before providing analysis".
    Verified live with qwen3.5:4b: after a truncated/overwhelming
    `read_paper` it ends the turn exactly like this, and from the graph's
    point of view the AIMessage has no real `tool_calls` — just text. That
    text is not an answer, so it should trigger the same retry path as a
    blank final message.

    Conservative on purpose: only fires when the message is basically a
    JSON blob with little other prose, or short prose that explicitly says
    the model is still mid-task — so a genuine answer that merely quotes
    some JSON isn't caught.
    """
    stripped = content.strip()
    if not stripped:
        return False

    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL)
    if fence:
        raw_json = fence.group(1)
        prose = (stripped[: fence.start()] + stripped[fence.end() :]).strip()
    else:
        brace = re.search(r"\{.*\}", stripped, re.DOTALL)
        if brace:
            raw_json = brace.group(0)
            prose = (stripped[: brace.start()] + stripped[brace.end() :]).strip()
        else:
            # No JSON at all — but short prose that only announces more work
            # ("Let me continue reading the paper before I answer.") is still
            # a non-answer.
            return len(stripped) < 400 and bool(_STALL_PHRASE_RE.search(stripped))

    # A stall phrase in the surrounding prose means the model is still
    # mid-task, no matter how long that prose is ("...to get a complete view
    # before providing analysis.").
    if _STALL_PHRASE_RE.search(prose):
        return True

    try:
        obj = json.loads(raw_json)
    except (ValueError, TypeError):
        obj = None

    if isinstance(obj, dict):
        has_name = any(k in obj for k in _TEXTUAL_TOOL_CALL_KEYS_NAME)
        has_args = any(k in obj for k in _TEXTUAL_TOOL_CALL_KEYS_ARGS)
        if has_name and has_args:
            return True
        if any(k in obj for k in _TEXTUAL_ACTION_KEYS):
            return True

    return False


def _is_empty_final(ai_message: AIMessage | None) -> bool:
    if ai_message is None or ai_message.tool_calls:
        return False
    content = ai_message.text if hasattr(ai_message, "text") else str(ai_message.content or "")
    if not content.strip():
        return True
    return _looks_like_textual_tool_call(content)


def _message_text(content: Any) -> str:
    if isinstance(content, list):
        parts = [block.get("text", "") if isinstance(block, dict) else str(block) for block in content]
        return "\n".join(parts).strip()
    return str(content or "").strip()


def _last_human_text(messages) -> str | None:
    """Finds the most recent HumanMessage's text, to quote verbatim in a
    nudge instead of asking the model to locate it itself — see
    NUDGE_MESSAGE_TEMPLATE's docstring in prompts/ensure_final_answer_prompt.py
    for why. Must be called on the original (pre-nudge) request messages,
    at the top of wrap_model_call/awrap_model_call, so it can never
    accidentally pick up a previously injected nudge instead of the real
    question.
    """
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            text = _message_text(msg.content)
            if text:
                return text
    return None


def _build_nudge(original_question: str | None) -> str:
    if not original_question:
        return NUDGE_MESSAGE
    return NUDGE_MESSAGE_TEMPLATE.format(question=original_question)


_DEFLECTION_PHRASE_RE = re.compile(
    r"("
    r"i don'?t see (a|any|your)[\w\s'-]{0,40}?(question|result|message)"
    r"|i (don'?t have|do not have) (a|any) result to summarize"
    r"|(there'?s|there is) no result to summarize"
    r"|no result to summarize"
    r"|how (would|can) (i|you) (like me to )?help"
    r"|what would you like me to (do|summarize|help)"
    r"|i see you'?ve shared"
    r"|this appears to be a new conversation"
    r")",
    re.IGNORECASE,
)


def _has_tool_result(messages) -> bool:
    return any(isinstance(msg, ToolMessage) for msg in messages)


def _is_deflection_despite_data(ai_message: AIMessage | None, messages) -> bool:
    """True when the model produced real text, but that text is a canned
    denial ("I don't see a result/question...") even though a tool already
    returned real data earlier in this same conversation.

    Verified live (`citation_graph`, points 8/9 of the memory-seeding test
    list, 5/5 reproductions): after `citation_graph` succeeds with real
    data, qwen3.5:4b can still end the turn with exactly this kind of
    denial — text `_is_empty_final` doesn't catch (it isn't empty, and
    isn't a described tool call), so without this check the turn used to
    end on a confidently wrong non-answer instead of retrying. Gated on
    `_has_tool_result` so a genuine "I don't understand your question" on a
    turn with no tool calls at all isn't misclassified as this specific
    failure.
    """
    if ai_message is None or ai_message.tool_calls:
        return False
    content = ai_message.text if hasattr(ai_message, "text") else str(ai_message.content or "")
    if not content.strip():
        return False
    return bool(_DEFLECTION_PHRASE_RE.search(content)) and _has_tool_result(messages)


def _needs_retry(ai_message: AIMessage | None, messages) -> bool:
    return _is_empty_final(ai_message) or _is_deflection_despite_data(ai_message, messages)


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


_OLLAMA_GENERATION_RETRIES = 2


def _call_with_ollama_retry(handler, request):
    """Calls `handler(request)`, retrying on an `ollama.ResponseError`.

    Verified live: `qwen3.5:4b` can generate a tool call with malformed
    XML-tagged syntax (an opening `<function>` tag closed with
    `</parameter>`) that Ollama's own `chat()` endpoint can't parse — it
    fails with an HTTP 500 (`ollama._types.ResponseError: XML syntax
    error...`), not a schema-level "invalid tool input" a retry-on-empty
    check ever sees, since no response comes back at all. This is a
    generation-format failure, not an application error, so a plain retry
    of the same request is the right first move — same spirit as the
    empty-response retry below, just for a different failure shape.
    Re-raises after `_OLLAMA_GENERATION_RETRIES` — `app.py`'s own
    exception handling already turns that into a short, friendly message
    instead of crashing the app.
    """
    attempts = 0
    while True:
        try:
            return handler(request)
        except OllamaResponseError:
            attempts += 1
            if attempts > _OLLAMA_GENERATION_RETRIES:
                raise
            logger.warning(
                "Ollama rejected a model-generated tool call (attempt %d/%d) — "
                "retrying the same request.",
                attempts, _OLLAMA_GENERATION_RETRIES, exc_info=True,
            )


async def _acall_with_ollama_retry(handler, request):
    attempts = 0
    while True:
        try:
            return await handler(request)
        except OllamaResponseError:
            attempts += 1
            if attempts > _OLLAMA_GENERATION_RETRIES:
                raise
            logger.warning(
                "Ollama rejected a model-generated tool call (attempt %d/%d) — "
                "retrying the same request.",
                attempts, _OLLAMA_GENERATION_RETRIES, exc_info=True,
            )


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
        nudge = _build_nudge(_last_human_text(request.messages))
        response = _call_with_ollama_retry(handler, current_request)
        attempts = 0

        while _needs_retry(_final_ai_message(response), current_request.messages) and attempts < self._max_retries:
            attempts += 1
            current_request = current_request.override(
                messages=[*current_request.messages, HumanMessage(content=nudge)]
            )
            response = _call_with_ollama_retry(handler, current_request)

        if not _needs_retry(_final_ai_message(response), current_request.messages):
            return response

        try:
            fallback_request = current_request.override(model=_get_fallback_model())
            response = _call_with_ollama_retry(handler, fallback_request)
            attempts = 0

            while _needs_retry(_final_ai_message(response), fallback_request.messages) and attempts < self._max_retries:
                attempts += 1
                fallback_request = fallback_request.override(
                    messages=[*fallback_request.messages, HumanMessage(content=nudge)]
                )
                response = _call_with_ollama_retry(handler, fallback_request)
        except Exception:
            logger.exception("Fallback model '%s' could not be called", _FALLBACK_MODEL_NAME)
            return _replace_ai_content(
                response, FALLBACK_MODEL_UNAVAILABLE_MESSAGE.format(model=_FALLBACK_MODEL_NAME)
            )

        if _needs_retry(_final_ai_message(response), fallback_request.messages):
            response = _replace_ai_content(response, FALLBACK_MESSAGE)

        return response

    async def awrap_model_call(
        self,
        request: "ModelRequest[Any]",
        handler: "Callable[[ModelRequest[Any]], Awaitable[ModelResponse[ResponseT]]]",
    ) -> "ModelResponse[ResponseT] | AIMessage":
        current_request = request
        nudge = _build_nudge(_last_human_text(request.messages))
        response = await _acall_with_ollama_retry(handler, current_request)
        attempts = 0

        while _needs_retry(_final_ai_message(response), current_request.messages) and attempts < self._max_retries:
            attempts += 1
            current_request = current_request.override(
                messages=[*current_request.messages, HumanMessage(content=nudge)]
            )
            response = await _acall_with_ollama_retry(handler, current_request)

        if not _needs_retry(_final_ai_message(response), current_request.messages):
            return response

        try:
            fallback_request = current_request.override(model=_get_fallback_model())
            response = await _acall_with_ollama_retry(handler, fallback_request)
            attempts = 0

            while _needs_retry(_final_ai_message(response), fallback_request.messages) and attempts < self._max_retries:
                attempts += 1
                fallback_request = fallback_request.override(
                    messages=[*fallback_request.messages, HumanMessage(content=nudge)]
                )
                response = await _acall_with_ollama_retry(handler, fallback_request)
        except Exception:
            logger.exception("Fallback model '%s' could not be called", _FALLBACK_MODEL_NAME)
            return _replace_ai_content(
                response, FALLBACK_MODEL_UNAVAILABLE_MESSAGE.format(model=_FALLBACK_MODEL_NAME)
            )

        if _needs_retry(_final_ai_message(response), fallback_request.messages):
            response = _replace_ai_content(response, FALLBACK_MESSAGE)

        return response


_TRACKED_ARXIV_TOOLS = {"get_abstract", "download_paper", "read_paper"}


def _tool_message_text(result: Any) -> str | None:
    if not isinstance(result, ToolMessage):
        return None
    content = result.content
    if isinstance(content, list):
        parts = [block.get("text", "") if isinstance(block, dict) else str(block) for block in content]
        return "\n".join(parts)
    return str(content) if content is not None else None


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
            new_fields["Local file"] = f"papers/raw/{paper_id}.md (full text retrieved)"

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
