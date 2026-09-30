from __future__ import annotations

import asyncio
import json
import logging
import re
import sqlite3
from typing import TYPE_CHECKING, Any

from langchain.agents.middleware.types import AgentMiddleware, ExtendedModelResponse, ModelResponse
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from langchain_ollama import ChatOllama
from ollama import ResponseError as OllamaResponseError

from prompts.ensure_final_answer_prompt import (
    NUDGE_MESSAGE,
    NUDGE_MESSAGE_TEMPLATE,
    NUDGE_MESSAGE_CALL_TOOL,
    NUDGE_MESSAGE_CALL_TOOL_TEMPLATE,
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
from memory.knowledge_graph import (
    GRAPH_DB_PATH,
    ensure_graph_schema,
    ingest_paper_entry,
    compute_keyword_similarity_edges,
    connect_hub_keywords,
)
from core.tools import read_skill
from core.arxiv_download import _CONTENT_WARNING, _CONTENT_WARNING_FOOTER
from memory.graph_tools import _GRAPH_LABEL_WARNING, _GRAPH_LABEL_WARNING_FOOTER

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


# Deliberately narrower than a bare "graph" trigger: the existing
# `citation_graph` arXiv tool is also routinely discussed in English using
# the word "graph" ("citation graph", "show me the graph of citations"),
# so matching plain "graph" here would misfire and inject the wrong
# skill. "grafo" (this user's own consistent Spanish wording for the
# knowledge graph throughout this project) and the exact phrase "knowledge
# graph" avoid that collision while still covering how it's actually asked
# about in practice.
_GRAPH_TRIGGER_RE = re.compile(r"\bgrafo\b|\bknowledge graph\b", re.IGNORECASE)

class _ForceSkillMiddleware(AgentMiddleware[Any, Any, Any]):
    """Deterministically injects a skill's full instructions right after
    the user's message when it matches `trigger`, instead of relying on the
    model to decide to call `read_skill` for it itself — same lesson, same
    mechanism as `ForcePaperAnalysisSkillMiddleware` above.

    Subclass per skill (set `skill_name`, `trigger`, `reason`) rather than
    instantiating this directly with parameters: LangChain identifies a
    middleware by its class name and refuses two instances of the same
    class ("Please remove duplicate middleware instances").

    Injected once per turn, not once per model call: the marker already
    appearing after the triggering HumanMessage is what stops the skill
    text from being re-inserted on every ReAct-loop call after the first.
    """

    skill_name: str
    trigger: "re.Pattern[str]"
    reason: str

    # Max calls per tool, counted over the current turn (everything after the
    # last HumanMessage), enforced in code only on turns whose message
    # matches `trigger`. 0 means the tool is off-limits for that skill.
    # Exists because a limit written in the skill's own text ("at most 3
    # searches") was verified live to be ignored: qwen3.5:4b made ~11 calls
    # on the first question, repeating one identical search four times and
    # drifting into arXiv network tools the skill says not to use.
    tool_limits: "dict[str, int]" = {}

    @property
    def _marker(self) -> str:
        return f"[auto-loaded: {self.skill_name} skill]"

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

        if not self.trigger.search(human_text):
            return request

        already_injected = any(
            isinstance(msg, SystemMessage) and self._marker in _message_text(msg.content)
            for msg in messages[last_human_idx + 1 :]
        )

        if already_injected:
            return request

        skill_text = read_skill.func(skill_name=self.skill_name)

        if skill_text.startswith("Error:"):
            logger.warning("%s: %s", type(self).__name__, skill_text)
            return request

        injected = SystemMessage(
            content=(
                f"{self._marker} The user's message {self.reason}, so the "
                f"{self.skill_name} skill's full instructions are loaded below "
                "automatically — you do not need to (and should not) call "
                "read_skill for it yourself. Follow these instructions for "
                "this turn:\n\n" + skill_text
            )
        )

        new_messages = list(messages)
        new_messages.insert(last_human_idx + 1, injected)

        return request.override(messages=new_messages)

    def _tool_call_rejection(self, request: "ToolCallRequest") -> str | None:
        """Why this tool call must not run, or None if it may.

        Only active on turns where the skill's trigger matched the user's
        message (the same condition that injects the skill). Blocked calls
        still count as attempts when numbering later calls, so once a limit
        is hit every further call to that tool stays blocked.
        """
        state = request.state
        messages = state.get("messages", []) if isinstance(state, dict) else getattr(state, "messages", [])

        last_human_idx = None
        for i in range(len(messages) - 1, -1, -1):
            if isinstance(messages[i], HumanMessage):
                last_human_idx = i
                break

        if last_human_idx is None:
            return None

        if not self.trigger.search(_message_text(messages[last_human_idx].content)):
            return None

        turn = messages[last_human_idx + 1 :]
        name = request.tool_call.get("name")
        this_id = request.tool_call.get("id")

        same_tool_calls = [
            tc for m in turn if isinstance(m, AIMessage) for tc in m.tool_calls if tc.get("name") == name
        ]
        position = next((i for i, tc in enumerate(same_tool_calls) if tc.get("id") == this_id), len(same_tool_calls))

        limit = self.tool_limits.get(name)

        if limit is not None and position >= limit:
            if limit == 0:
                return (
                    f"'{name}' is not available for this request ({self.skill_name} skill). "
                    "Use only the tools that skill lists, and answer with what you already have."
                )
            return (
                f"Tool call limit reached: '{name}' can be called at most {limit} time(s) for this "
                f"request ({self.skill_name} skill). Do not call it again — write your answer from "
                "the results you already have."
            )

        results = {m.tool_call_id: m for m in turn if isinstance(m, ToolMessage)}

        for earlier in same_tool_calls[:position]:
            previous = results.get(earlier.get("id"))
            if earlier.get("args") == request.tool_call.get("args") and previous is not None and previous.status != "error":
                return (
                    f"You already made this exact '{name}' call in this request and it succeeded. "
                    "Do not repeat it — use its result above."
                )

        return None

    def wrap_tool_call(
        self,
        request: "ToolCallRequest",
        handler: "Callable[[ToolCallRequest], ToolMessage | Any]",
    ) -> "ToolMessage | Any":
        rejection = self._tool_call_rejection(request)
        if rejection:
            logger.info("%s blocked %s: %s", type(self).__name__, request.tool_call.get("name"), rejection)
            return ToolMessage(
                content=rejection,
                name=request.tool_call.get("name"),
                tool_call_id=request.tool_call["id"],
                status="error",
            )
        return handler(request)

    async def awrap_tool_call(
        self,
        request: "ToolCallRequest",
        handler: "Callable[[ToolCallRequest], Awaitable[ToolMessage | Any]]",
    ) -> "ToolMessage | Any":
        rejection = self._tool_call_rejection(request)
        if rejection:
            logger.info("%s blocked %s: %s", type(self).__name__, request.tool_call.get("name"), rejection)
            return ToolMessage(
                content=rejection,
                name=request.tool_call.get("name"),
                tool_call_id=request.tool_call["id"],
                status="error",
            )
        return await handler(request)


class ForceGraphSkillMiddleware(_ForceSkillMiddleware):
    """Injects `knowledge-graph` when the message mentions "grafo"/"knowledge
    graph".

    Verified live: even with a hardened GRAPH_PROMPT (an explicit worked
    example, an explicit "these are real tool calls, never write one out
    as text" warning) baked into the system prompt on every turn,
    qwen3.5:4b, llama3.2:3b, and cogito:8b all still failed to actually
    call the graph tools — but that run was later found to be a
    truncated-context artifact (num_ctx below the prompt size, see
    MIN_RECOMMENDED_NUM_CTX in graph.py), so how much this injection adds
    on its own is unproven: the same question also succeeded with the
    injection disabled (one run each).
    """

    skill_name = "knowledge-graph"
    trigger = _GRAPH_TRIGGER_RE
    reason = "mentions the knowledge graph"


# Spanish and English phrasings of "look for what argues against my
# conclusion". Kept to explicit, unambiguous phrases (not a bare "against"
# or "contra") so an ordinary sentence doesn't load a skill it doesn't need.
_CHALLENGE_TRIGGER_RE = re.compile(
    r"evidencia en contra|contra-?evidencia|counter-?evidence|evidence against"
    r"|abogado del diablo|devil'?s advocate|poke holes|\brefut"
    r"|challenge (my|this|the|our) (conclusion|hypothesis|claim|view)"
    r"|cuestiona (mi|esta|la|nuestra) (conclusi|hip[oó]tesis|idea)"
    r"|qu[eé] podr[ií]a estar mal|what could be wrong",
    re.IGNORECASE,
)


# arXiv-network and full-text tools that the two evidence skills must not
# reach for: their whole method is "retrieve passages from the papers
# already downloaded", and these are the tools the model drifted into.
_NO_ARXIV_LOOKUPS = {
    name: 0
    for name in (
        "search_papers", "list_papers", "get_abstract", "download_paper", "read_paper",
        "citation_graph", "export_citations", "watch_topic", "check_alerts", "list_watches",
        "unwatch_topic", "get_paper_latex", "list_paper_latex_sections", "get_paper_latex_section",
        "get_paper_outline", "read_paper_section", "search_paper_text",
    )
}


class ForceChallengeSkillMiddleware(_ForceSkillMiddleware):
    """Injects `challenge-conclusion` when the user asks for evidence against
    a conclusion they're leaning toward.
    """

    skill_name = "challenge-conclusion"
    trigger = _CHALLENGE_TRIGGER_RE
    reason = "asks for evidence against a conclusion"
    tool_limits = {**_NO_ARXIV_LOOKUPS, "search_paper_content": 3, "search_memory": 1}


# "Do these two papers disagree / are they comparable". Requires either the
# word "papers" (or an arXiv id) near a compare verb, or an explicit
# agree/disagree/contradict phrase, so a bare "compare" (models, prices…)
# doesn't load it.
_COMPARE_TRIGGER_RE = re.compile(
    r"se contradicen|se contradice\b|discrepan|discrepancia|\bdisagree|contradict"
    r"|difieren|\bdo (these|the|both|they)\b[^.?!]{0,40}\b(agree|disagree|conflict)"
    r"|compar\w*\b[^.?!]{0,40}\b(papers?|art[ií]culos|estudios)"
    r"|compar\w*\b[^.?!]{0,80}\b\d{4}\.\d{4,5}",
    re.IGNORECASE,
)


class ForceCompareSkillMiddleware(_ForceSkillMiddleware):
    """Injects `compare-papers` when the user asks whether two papers agree,
    contradict each other, or can be compared.
    """

    skill_name = "compare-papers"
    trigger = _COMPARE_TRIGGER_RE
    reason = "asks whether two papers agree or can be compared"
    tool_limits = {**_NO_ARXIV_LOOKUPS, "search_paper_content": 4, "search_graph_nodes": 2}


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
    # Spanish equivalents — this agent's replies aren't forced to English
    # (verified live: qwen3.5:4b answers in whatever language the user
    # wrote in), and the English-only patterns above silently missed a
    # real "described, not executed" turn that happened to be in Spanish
    # ("Voy a empezar buscando el paper...").
    r"|voy a (empezar|continuar|seguir|buscar|revisar|comprobar|explorar)"
    r"|primero (necesito|voy a|debo)"
    r"|antes de (responder|dar|proporcionar|continuar)"
    # More "narrated a call instead of making one" phrasings — verified
    # live with llama3.2:3b (the EnsureFinalAnswerMiddleware fallback
    # model) on the same graph-tools question: "Here's the tool call: "
    # + a single-backtick call + "Please wait for the result..." — none
    # of the phrases above matched this exact wording.
    r"|here'?s the tool call"
    r"|here is the tool call"
    r"|wait for the result"
    r"|i'?ll (call|invoke)"
    r"|let'?s call"
    r")\b",
    re.IGNORECASE,
)

# A code span containing a bare `name(args)` call — not JSON — is just as
# clear a sign the model described a tool call instead of issuing one.
# Matches both a triple-backtick fence (verified live: qwen3.5:4b ended a
# turn with a fence containing exactly `search_graph_nodes(query=
# "Attention Is All You Need")`) and a single-backtick inline span
# (verified live: llama3.2:3b did the same with `search_paper_text(...)`
# in single backticks — the fence-only version of this regex missed it
# entirely since there's no triple-backtick fence at all). Neither case
# has a `{`, so the JSON-fence/brace checks below don't catch either one.
#
# Requires an underscore in the identifier: every real tool name in this
# codebase is snake_case (search_graph_nodes, download_paper, ...), while
# a genuine answer can legitimately contain single-word inline code like a
# formula (`loss(x) = -log(p)`) — verified this exact string was a false
# positive without the underscore requirement.
_FUNCTION_CALL_FENCE_RE = re.compile(
    r"```(?:\w+)?\s*\n?\s*[A-Za-z_][A-Za-z0-9]*_[A-Za-z0-9_]*\s*\([^`]*\)\s*```"
    r"|`[A-Za-z_][A-Za-z0-9]*_[A-Za-z0-9_]*\s*\([^`\n]*\)`",
    re.DOTALL,
)

# The same call, with no backticks at all — the whole message is just the
# bare expression `tool_name(args)`. Verified live with qwen3.5:4b on the
# knowledge-graph tools: a short, single-hop question produced exactly
# `search_graph_nodes(query="Attention Is All You Need")` as the ENTIRE
# message, no prose, no fence — evading every check above (no backticks,
# no stall phrase, well under the 400-char prose fallback but that branch
# only fires via _STALL_PHRASE_RE, which this text never matches either).
# fullmatch on the whole stripped message, so a genuine answer that merely
# mentions a snake_case-looking call somewhere in a longer sentence is
# never affected — only a message that IS just the call, nothing else.
_BARE_FUNCTION_CALL_RE = re.compile(
    r"[A-Za-z_][A-Za-z0-9]*_[A-Za-z0-9_]*\s*\(.*\)\.?",
    re.DOTALL,
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

    if _FUNCTION_CALL_FENCE_RE.search(stripped):
        return True

    if _BARE_FUNCTION_CALL_RE.fullmatch(stripped):
        return True

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


def _build_nudge(original_question: str | None, has_tool_result: bool) -> str:
    """Two different nudges for two different problems, both caught by
    _needs_retry: `has_tool_result=True` means a tool already ran and the
    model just needs to summarize/use that real data (telling it not to
    call more tools prevents re-looping the same call); `False` means no
    tool has actually run yet — the model only described one in text — so
    the nudge must push it to make a REAL call, not forbid calling one.
    """
    if has_tool_result:
        if not original_question:
            return NUDGE_MESSAGE
        return NUDGE_MESSAGE_TEMPLATE.format(question=original_question)
    if not original_question:
        return NUDGE_MESSAGE_CALL_TOOL
    return NUDGE_MESSAGE_CALL_TOOL_TEMPLATE.format(question=original_question)


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

_fallback_model_cache: dict = {}

def _get_fallback_model(num_ctx: int | None = None) -> ChatOllama:
    # num_ctx must match the selected model's: without it Ollama falls back
    # to its 4096 default, and the agent's full prompt (system prompt +
    # tool schemas, ~16k tokens) was verified in Ollama's server log to be
    # truncated to 2050 tokens, keeping only the first 4 — the fallback
    # then never saw the system prompt or any tool definition at all.
    if num_ctx not in _fallback_model_cache:
        # temperature=0: this tier only runs when the selected model has
        # already failed to produce a final answer twice, so the goal is
        # a plain, reliable response, not variety.
        kwargs = {"num_ctx": num_ctx} if num_ctx else {}
        _fallback_model_cache[num_ctx] = ChatOllama(model=_FALLBACK_MODEL_NAME, temperature=0, **kwargs)
    return _fallback_model_cache[num_ctx]


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


# --- Output guardrail: neutralize auto-loading markdown images ------------------------
# SECURITY_IMPLEMENTATION_PLAN.md step 4.2, closing SECURITY_REVIEW.md finding #6
# (confirmed live in step 4.1, not just theorized): a markdown image `![alt](url)` in the
# model's own reply auto-loads the instant Chainlit renders it — no click needed — and
# `.chainlit/config.toml`'s `unsafe_allow_html = false` does NOT stop this, since it only
# blocks raw HTML/`<script>`, not standard markdown image syntax. Verified with a real
# local logging server: a crafted reply produced two real outbound GET requests, query
# string intact, confirmed both in the browser's own network panel and in the page's
# accessibility tree (a genuine <img> element, not text).
#
# The regex, the placeholder and the stripping live in core/image_guard.py (shared with
# app.py). IMPORTANT — this middleware alone is NOT enough for the real app, which was only
# discovered after step 4.2 had been marked done: it sanitizes the FINISHED AIMessage, but
# app.py streams each token to the browser as the model generates it (inside the model call,
# before this runs), and the image renders the instant its closing ")" arrives. The
# streamed path is covered by MarkdownImageStreamFilter in app.py; this stays as a
# defense-in-depth layer for everything that reads the agent's messages (checkpoints,
# history, any future non-streaming client).
from core.image_guard import (  # noqa: E402
    BLOCKED_IMAGE_PLACEHOLDER as _BLOCKED_IMAGE_PLACEHOLDER,
    MARKDOWN_IMAGE_RE as _MARKDOWN_IMAGE_RE,
    strip_markdown_images as _strip_markdown_images,
)


class OutputImageGuardrailMiddleware(AgentMiddleware[Any, Any, Any]):
    """Neutralizes markdown image syntax in the model's own output before it can ever
    reach the browser.

    Deliberately unconditional — every markdown image gets stripped, not just ones
    pointing at some "untrusted domain" list. This agent's answers are text; they never
    legitimately need to embed a live-loading image. Trying to maintain an allowlist of
    "safe" domains would be weaker than simply never letting this syntax render at all —
    a model echoing attacker-controlled text (from a hostile paper, from anywhere) can put
    any string it likes in a URL, including one crafted to merely look trustworthy.

    Placed FIRST in graph.py's middleware list — deliberately outermost. LangChain
    composes wrap_model_call middleware with the first-listed one outermost (same rule
    verified for wrap_tool_call in UntrustedContentMiddleware's own comment — see
    langchain.agents.factory._chain_model_call_handlers), meaning it's the LAST thing to
    touch the response on the way out. That matters here: this has to run after
    EnsureFinalAnswerMiddleware's own retries/fallback have already settled on the actual
    final answer, not sanitize a draft that then gets discarded and replaced anyway.
    """

    def wrap_model_call(
        self,
        request: "ModelRequest[Any]",
        handler: "Callable[[ModelRequest[Any]], ModelResponse[Any]]",
    ) -> "ModelResponse[Any]":
        return self._maybe_sanitize(handler(request))

    async def awrap_model_call(
        self,
        request: "ModelRequest[Any]",
        handler: "Callable[[ModelRequest[Any]], Awaitable[ModelResponse[ResponseT]]]",
    ) -> "ModelResponse[ResponseT] | AIMessage":
        return self._maybe_sanitize(await handler(request))

    def _maybe_sanitize(self, response: Any) -> Any:
        message = _final_ai_message(response)
        if message is None:
            return response

        original = _message_text(message.content)
        if not original or "![" not in original:
            return response  # fast path — skip the regex entirely for the common case

        sanitized = _strip_markdown_images(original)
        if sanitized == original:
            return response

        logger.warning("OutputImageGuardrailMiddleware: blocked a markdown image in the model's own output")
        return _replace_ai_content(response, sanitized)


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
        nudge = _build_nudge(_last_human_text(request.messages), _has_tool_result(request.messages))
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
            fallback_request = current_request.override(
                model=_get_fallback_model(getattr(request.model, "num_ctx", None))
            )
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
        nudge = _build_nudge(_last_human_text(request.messages), _has_tool_result(request.messages))
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
            fallback_request = current_request.override(
                model=_get_fallback_model(getattr(request.model, "num_ctx", None))
            )
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


# --- Untrusted-content wrapping (SECURITY_IMPLEMENTATION_PLAN.md, step 1.3) -------------

# Tool names whose result gets wrapped with the same untrusted-content framing
# `download_paper` used to apply only to its own output, manually, inside
# core/arxiv_download.py's _success_payload (_CONTENT_WARNING header +
# _CONTENT_WARNING_FOOTER). SECURITY_REVIEW.md found that warning applied to only 1 of 8+
# tools that return a paper's actual text — the rest of the arxiv-mcp-server tool set
# (search_papers, get_abstract, read_paper, list_papers, citation_graph) had none at all.
#
# download_paper is included here too, not just the 5 new ones: _success_payload's own
# manual wrapping was removed (core/arxiv_download.py) once this middleware could reproduce
# it, so this set is now the ONLY source of this warning for all six — no tool wraps its own
# output anymore, which is the point (a seventh tool added later only needs its name added
# here, not its own copy of this logic).
#
# watch_topic/check_alerts (also arxiv-mcp-server) are deliberately NOT here yet: they
# return topic-monitoring metadata (new-paper alerts), not a paper's own prose, so whether
# they need the same framing is a separate question for a later pass, not assumed here.
#
# The first six return a JSON payload (status/message/paper_id/... plus one field with the
# actual text), not plain prose directly — wrapping the whole raw string, as `_maybe_wrap`
# below does, means the header lands before the opening `{` and the footer after the
# closing `}`, not hugging just the text field. Structurally this is fine for the actual
# goal (the footer is now the literal last thing before the model resumes generating, for
# every one of these tools uniformly) and it keeps this middleware simple and tool-agnostic
# — the tradeoff is that the JSON the model sees is no longer strictly parseable JSON on its
# own. Verified live against qwen3.5:4b for both download_paper and get_abstract (step 1.2):
# it reads past the non-strict-JSON framing fine, doesn't quote the wrapper back, doesn't
# comment on it, extracts the real content correctly.
#
# search_paper_content (memory/paper_rag.py) is different in shape — added in step 1.3, the
# most-used research tool per prompts/arxiv_prompt.py and the only one of these seven a
# small model is explicitly told to reach for by default. It returns PLAIN TEXT already (up
# to 5 parent chunks, each prefixed with a "Title/Authors/arXiv id" header, joined by
# "\n\n---\n\n"), never JSON — so it doesn't have the non-strict-JSON tradeoff above at all,
# wrapping the whole string is exactly as clean as wrapping a single passage would be. It's
# wrapped ONCE around the whole multi-passage result (header once, footer once), not
# per-passage: matches how a long download_paper/read_paper result is already wrapped as one
# block regardless of how many internal sections it has, and keeps the per-call context cost
# fixed instead of multiplying with `k` (up to 20). If a future live test finds the header
# isn't "sticky" across 5 unrelated passages the way the footer already is by sitting right
# at the end, per-passage repetition is the next thing to try — not assumed necessary here.
#
# analyze_paper_figures (core/figure_analysis.py) added in step 4.4, same JSON shape as the
# original six (status/paper_id/... plus a "figures" list of {page, index, description}).
# SECURITY_REVIEW.md finding #7: a PDF page can contain what looks like a figure but is
# actually text rendered as an image (invisible to every text-based tool, since it was never
# text) — the local vision model reads it and transcribes/describes it, and that description
# is exactly the kind of untrusted external content the other six tools already carry the
# same wrapper for. The plan's own step 4.4 originally scoped this as prompt-text-only (a
# paragraph in FIGURE_ANALYSIS_PROMPT, prompts/arxiv_prompt.py) — added here instead/also,
# once it was clear a prompt-only note repeats exactly the mistake finding #1 already
# documented (a warning that isn't backed by code is the thing this whole middleware exists
# to stop relying on). No vision-capable model is installed in this dev environment, so this
# couldn't be verified live end-to-end the way download_paper/get_abstract were in step 1.2
# — only structurally, against a synthetic result matching this tool's real JSON shape.
_UNTRUSTED_CONTENT_TOOLS: frozenset[str] = frozenset({
    "download_paper",
    "search_papers",
    "get_abstract",
    "read_paper",
    "list_papers",
    "citation_graph",
    "analyze_paper_figures",
    "search_paper_content",
})

# Step 1.4: the four graph tools (memory/graph_tools.py) — search_graph_nodes,
# get_node_neighbors, list_nodes_by_type, find_similar_keywords. Kept as a SEPARATE set
# from _UNTRUSTED_CONTENT_TOOLS, with its own short header/footer
# (_GRAPH_LABEL_WARNING/_GRAPH_LABEL_WARNING_FOOTER, defined in memory/graph_tools.py),
# rather than folded into the same set with the long _CONTENT_WARNING: these tools return a
# handful of node labels or an id/weight list, not paper prose, and the long warning's
# LaTeX-markup/"don't complete this document" caveats don't apply to that shape of content
# at all — a one-line "these labels came from external text" note carries the same "treat as
# data, not instructions" framing without burying a short result under a paragraph written
# for a very different one. See SECURITY_REVIEW.md finding #4: a node label is permanent
# once ingested (memory/knowledge_graph.py extracts it from a paper's own title/abstract via
# KeyBERT) and resurfaces in every future conversation that queries the graph, not just the
# one where the paper was first read.
_UNTRUSTED_LABEL_TOOLS: frozenset[str] = frozenset({
    "search_graph_nodes",
    "get_node_neighbors",
    "list_nodes_by_type",
    "find_similar_keywords",
})


class UntrustedContentMiddleware(AgentMiddleware[Any, Any, Any]):
    """Wraps the result of any tool named in `_UNTRUSTED_CONTENT_TOOLS` (long framing,
    `_CONTENT_WARNING`/`_CONTENT_WARNING_FOOTER` from core/arxiv_download.py) or
    `_UNTRUSTED_LABEL_TOOLS` (short framing, `_GRAPH_LABEL_WARNING`/
    `_GRAPH_LABEL_WARNING_FOOTER` from memory/graph_tools.py) — the same prompt-injection
    framing already verified live to matter for `download_paper`: a header alone wasn't
    "sticky" enough for qwen3.5:4b over a long document, the footer right where generation
    resumes is what actually closed that gap (see core/arxiv_download.py's docstring).

    Centralizing this here, driven by name sets, is the fix for the gap SECURITY_REVIEW.md
    documents: a tool that returns external content only needs its name added to the right
    set, not its own copy of this wrapping — so the next tool added to the agent can't
    quietly ship without this protection the way search_paper_content and the arxiv-mcp-
    server tools did.
    """

    def wrap_tool_call(
        self,
        request: "ToolCallRequest",
        handler: "Callable[[ToolCallRequest], ToolMessage | Any]",
    ) -> "ToolMessage | Any":
        result = handler(request)
        return self._maybe_wrap(request, result)

    async def awrap_tool_call(
        self,
        request: "ToolCallRequest",
        handler: "Callable[[ToolCallRequest], Awaitable[ToolMessage | Any]]",
    ) -> "ToolMessage | Any":
        result = await handler(request)
        return self._maybe_wrap(request, result)

    def _maybe_wrap(self, request: "ToolCallRequest", result: Any) -> Any:
        name = request.tool_call.get("name")

        if name in _UNTRUSTED_CONTENT_TOOLS:
            header, footer = _CONTENT_WARNING, _CONTENT_WARNING_FOOTER
        elif name in _UNTRUSTED_LABEL_TOOLS:
            header, footer = _GRAPH_LABEL_WARNING, _GRAPH_LABEL_WARNING_FOOTER
        else:
            return result

        text = _tool_message_text(result)
        if not text or text.startswith(header):
            # Not a ToolMessage with text content, or already wrapped upstream — never
            # wrap the same result twice.
            return result

        return ToolMessage(
            content=header + text + footer,
            tool_call_id=result.tool_call_id,
            name=result.name,
            status=result.status,
        )


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

        # SECURITY_IMPLEMENTATION_PLAN.md step 2.1 (provenance tagging, closes
        # SECURITY_REVIEW.md finding #3 — memory poisoning): Title/Authors/Abstract below
        # come straight from an arXiv paper this middleware never verified beyond "the tool
        # call succeeded" — a hostile paper's own wording could be sitting in any of those
        # fields. Tagging the entry here, once, at the only place a paper's fields ever get
        # written into long-term memory, means every future search_memory hit on it carries
        # this marker too (step 2.2 reads it back out and re-applies a warning) instead of
        # this text quietly becoming indistinguishable from a note the agent wrote with its
        # own judgment. Fixed value, not model-decided — same reasoning as the rest of this
        # class: don't leave something this load-bearing to a prompt instruction.
        # Note: this also organically back-fills older entries that predate this field —
        # any paper touched again after this change (e.g. download_paper on one already
        # saved via get_abstract) goes through the merge branch below, which adds this key
        # to the existing entry the same as any other updated field. No separate migration
        # script needed for an entry that gets touched again; step 2.3 covers the rest.
        new_fields = {"arXiv ID": paper_id, "Source": "external (arXiv), unverified"}

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
            final_fields = new_fields
            content = _format_kv_block(final_fields)
            if content:
                update_memory.func(content=content, category="paper")
        else:
            final_fields = _parse_kv_block(existing["content"])
            final_fields.update({key: value for key, value in new_fields.items() if value})
            edit_memory.func(entry_id=existing["id"], content=_format_kv_block(final_fields), category="paper")

        self._update_knowledge_graph(final_fields)

    def _update_knowledge_graph(self, fields: dict) -> None:
        """Adds/updates this one paper's nodes and edges in graph.sqlite the
        moment it's saved to long-term memory — the same deterministic,
        no-model-decision-needed philosophy as the rest of this class.

        Runs `ingest_paper_entry`, `compute_keyword_similarity_edges`, and
        `connect_hub_keywords` synchronously, right here, every time.
        Measured live against the real graph (1,154 keyword nodes): the
        pairwise similarity pass takes ~4.2s (vectorized cosine similarity
        via sentence-transformers/torch, not a Python loop) and the hub
        pass is effectively instant — negligible next to a model turn that
        already takes 10-60s. The `python -m memory.knowledge_graph`
        script's 1-2 minute runtime was never about this step; it comes
        from re-running KeyBERT extraction over every paper in the corpus,
        and `ingest_paper_entry` already only extracts keywords for this
        one paper.

        This is O(n^2) in the number of keyword nodes (every keyword
        compared against every other), so it will need revisiting — e.g.
        comparing only this paper's new keywords against existing ones,
        instead of all-against-all — if the corpus grows an order of
        magnitude past where it is now; not a concern at the current size.

        Failure here must never affect the memory write above, which is
        the already-verified, primary behavior — caught and logged on its
        own rather than left to propagate into `_maybe_record_paper`'s
        wrapping try/except, whose log message is worded for the memory
        write, not this.
        """

        try:
            GRAPH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(GRAPH_DB_PATH), timeout=30)
            try:
                ensure_graph_schema(conn)
                ingest_paper_entry(conn, fields)
                compute_keyword_similarity_edges(conn)
                connect_hub_keywords(conn)
                conn.commit()
            finally:
                conn.close()
        except Exception:
            logger.exception(
                "Failed to update knowledge graph for paper %s", fields.get("arXiv ID")
            )


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
