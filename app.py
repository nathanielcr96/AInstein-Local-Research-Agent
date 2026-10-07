import sys
import asyncio
import chainlit as cl
import json
import logging
import time
import uuid
import httpx
import ollama
from chainlit.types import ThreadDict

# Paper content (abstracts, titles) routinely contains non-ASCII characters
# (Greek letters, accents) — on Windows, stdout/stderr default to the
# console's codepage (cp1252), which crashes with UnicodeEncodeError the
# moment any such character reaches a plain print()/log call. Forcing UTF-8
# here, as early as possible, protects every print/log path in this process,
# not just our own.
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
from graph import build_agent, MAX_NUM_CTX, MIN_RECOMMENDED_NUM_CTX, MEASURED_PROMPT_TOKENS
from core.ollama_functions import get_ollama_models_info, extract_llm_metrics
from core.huggingface_functions import get_huggingface_models_info
from core.chainlit_data import build_data_layer, authenticate_local_user
from core.companion_apps import launch_companion_apps
from core.image_guard import MarkdownImageStreamFilter, strip_markdown_images
from core.injection_detector import detect_injection, format_notice
from core.middleware import (
    _MEMORY_WRITE_TOOLS,
    _UNTRUSTED_CONTENT_TOOLS,
    _UNTRUSTED_LABEL_TOOLS,
    pop_blocked_memory_writes,
)
from core import external_check, memory_proposals, output_check
from observability.metrics_store import log_turn
import pandas as pd

logger = logging.getLogger(__name__)

# Starts the observability dashboard / knowledge graph Streamlit apps in
# the background so the header buttons (.chainlit/config.toml) work
# immediately, without the user having to open two more terminals
# themselves. Runs once per process start (module-level, not inside a
# request/session handler) and is a no-op if they're already running —
# see core/companion_apps.py for why that matters under --watch reloads.
launch_companion_apps()

# Enables the thread-history sidebar and chat resume. See
# core/chainlit_data.py for why header_auth_callback is used to satisfy
# Chainlit's auth requirement without an actual login page.
cl.data_layer(build_data_layer)
cl.header_auth_callback(authenticate_local_user)

# Tracks the single in-flight main() task, if any. This app has exactly one
# local user (see core/chainlit_data.py), so a brand new on_chat_start/
# on_chat_resume almost always means the previous browser tab/session was
# abandoned (closed, refreshed, or reconnected after a long silent wait —
# e.g. a model's first cold load into Ollama, which can take a minute-plus
# with no visible progress) rather than a deliberate second conversation.
# The old task would otherwise keep running unseen: still holding an Ollama
# request slot, still writing to the checkpointer/data layer, needlessly
# competing with the new session's own first message. Cancelling it here
# is what stops that competition from compounding the very wait that
# likely caused the reconnect in the first place.
_active_message_task: asyncio.Task | None = None

def _cancel_previous_message_task() -> None:
    global _active_message_task
    if _active_message_task is not None and not _active_message_task.done():
        _active_message_task.cancel()
    _active_message_task = None

def _build_embedding_options() -> list[str]:
    """
    Combines Ollama and HuggingFace embedding models into a single flat
    list of bare names for the dropdown — which backend serves a given
    model is an implementation detail the user shouldn't need to care
    about. `_resolve_embedding_selection` re-derives the provider for
    whichever name gets selected, by checking which catalog it came from.
    """

    ollama_models = get_ollama_models_info()
    hf_models = get_huggingface_models_info()

    options = [name for name, info in ollama_models.items() if info["is_embedding"]]
    options += [name for name, info in hf_models.items() if info["is_embedding"]]

    return options

def _resolve_embedding_selection(name: str | None) -> tuple[str | None, str | None]:
    """
    Looks up which provider actually serves the selected embedding model
    name, since the dropdown no longer carries that as a prefix.
    """

    if not name:
        return None, None

    ollama_models = get_ollama_models_info()
    if name in ollama_models and ollama_models[name]["is_embedding"]:
        return "ollama", name

    hf_models = get_huggingface_models_info()
    if name in hf_models and hf_models[name]["is_embedding"]:
        return "huggingface", name

    return None, None

def _format_tool_output(output) -> str:
    """
    Normalizes a tool's output for display in the UI Step.

    Regular tools (read_skill, memory...) return `content` as a
    plain string. MCP tools (the arXiv ones) return it as a list of
    blocks (e.g. [{"type": "text", "text": "..."}]) — without normalizing
    this, the Step showed the Python repr instead of readable text. This
    also covers the case where `output` doesn't have `.content` at all
    (previously caused an UnboundLocalError further down).
    """

    content = output.content if hasattr(output, "content") else output

    if isinstance(content, list):

        parts = []

        for block in content:

            if isinstance(block, dict) and "text" in block:
                parts.append(str(block["text"]))
            else:
                parts.append(str(block))

        return "\n".join(parts)

    return str(content)

def _extract_tool_status(output) -> str:
    """
    Best-effort read of whether a tool call actually succeeded, for the
    observability dashboard's success/error breakdown. Two sources, in
    order: (1) `ToolMessage.status`, set explicitly to "error" by
    `ExcludeToolsMiddleware`/`ArxivTimeoutMiddleware` when they reject or
    time out a call before it ever reaches the real tool; (2) a "status"
    field in the tool's own JSON output — most tools in this project
    (`citation_graph`, `search_papers`, `download_paper`...) report
    success/error/rate_limited this way even when the LangChain-level call
    itself didn't raise. Defaults to "success" when neither is present,
    which covers plain-text tools (`read_skill`, `search_paper_content`)
    that have no notion of partial failure to report.
    """

    status = getattr(output, "status", None)

    if status == "error":
        return "error"

    try:
        payload = json.loads(_format_tool_output(output))
    except (json.JSONDecodeError, TypeError):
        return "success"

    if isinstance(payload, dict) and isinstance(payload.get("status"), str):
        return payload["status"]

    return "success"

def _friendly_error_message(exc: Exception) -> str:
    """
    Short, non-technical message for the user. The full detail
    (traceback) always goes to the console via logger.exception, never to
    the chat.
    """

    if isinstance(exc, httpx.ConnectError):
        return "Could not connect to Ollama. Check that the service is running (`ollama serve`)."

    if isinstance(exc, ollama.ResponseError):
        return f"Ollama returned an error: {exc.error}"

    if isinstance(exc, KeyError):
        return f"The selected model is no longer available in Ollama ({exc})."

    return f"{type(exc).__name__}: {str(exc)[:200]}"

async def _send_chat_settings() -> None:

    models_info = get_ollama_models_info()

    # Only models with the "completion" capability — mxbai-embed-large,
    # for example, used to show up in this same dropdown even though it's
    # not usable for chat (it's an embedding model, capability "embedding").
    chat_models_names = [
        name for name, info in models_info.items() if info["is_chat"]
    ]

    embedding_options = _build_embedding_options()

    await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="model",
                label="Model",
                values=chat_models_names,
                initial_index=0
            ),

            cl.input_widget.Select(
                id="embedding_model",
                label="Embedding Model",
                values=embedding_options if embedding_options else ["(none available)"],
                initial_index=0
            ),

            cl.input_widget.Slider(
                id="temperature",
                label="Temperature",
                initial=0,
                min=0,
                max=1,
                step=0.1
            ),

            cl.input_widget.Switch(
                id="memory",
                label="Memory (remember previous messages from this conversation)",
                initial=False
            ),

            cl.input_widget.Switch(
                id="streaming",
                label="Streaming",
                initial=True
            )
        ]
    ).send()

@cl.on_chat_start
async def start():

    _cancel_previous_message_task()

    await _send_chat_settings()

@cl.on_chat_resume
async def resume(thread: ThreadDict):
    # cl.context.session.thread_id is already restored to this thread's id
    # by Chainlit itself (see Session.__init__) before this runs, so main()
    # picking it up is enough to reconnect to the exact same LangGraph
    # checkpoint state (checkpoints.sqlite) this thread had. Chat settings
    # (model, embeddings, switches) aren't part of that persisted state
    # though, so they need to be re-sent for the user to pick again.
    _cancel_previous_message_task()

    await _send_chat_settings()

async def _check_reply_for_steering(user_question: str, reply: str) -> None:
    """After a turn that read outside text: ask the decision model whether the reply pushes the person
    toward something they didn't ask for, and say so in the chat if it does. Notice only — see
    core/output_check.py. Silent when `nimble` is not installed or anything goes wrong."""
    try:
        verdict = await asyncio.to_thread(output_check.check_reply, user_question, reply)
        if not verdict.flagged:
            logger.info("Reply check: %s", verdict.reason)
            return
        logger.warning("Reply check flagged the reply (%s, p=%.2f)", verdict.category, verdict.probability)
        await cl.Message(content=output_check.format_notice(verdict), author="Security notice").send()
    except Exception:
        logger.exception("Reply check failed (does not affect the answer)")


async def _check_external_text(results: list[tuple[str, str]]) -> None:
    """After a turn that read outside text: a second opinion on the passages the phrase detector let
    through. Notice only — see core/external_check.py. Silent when `nimble` is not installed or anything
    goes wrong."""
    try:
        findings = await asyncio.to_thread(external_check.check_turn, results)
        if not findings:
            return
        logger.warning("External text check flagged %d passage(s) (%s)", len(findings), sorted({f.tool for f in findings}))
        await cl.Message(content=external_check.format_notice(findings), author="Security notice").send()
    except Exception:
        logger.exception("External text check failed (does not affect the answer)")


_MAX_PENDING_SUGGESTIONS = 5


async def _offer_memory_suggestion(text: str, model_already_saved: bool) -> None:
    """After the answer: if the person's own message states something lasting, offer to save it.

    Everything that matters is in core/memory_proposals.py — code rules first, the `nimble` decision
    model as a veto/label, the exact text in the buttons' message, and a click required. The model
    that answers the chat is not involved. With `nimble` not installed this is a silent no-op.
    """
    if model_already_saved:
        return
    try:
        decision = await asyncio.to_thread(memory_proposals.decide, text)
        if not decision.propose:
            logger.info("No memory suggestion: %s", decision.reason)
            return

        # The buttons carry only an id; the text and category stay server-side, so nothing a client
        # sends back can change what gets written. One use each.
        suggestion_id = uuid.uuid4().hex
        replaces = decision.replaces  # an entry of yours this message looks like a newer version of, or None
        actions = []
        if replaces:
            actions.append(cl.Action(name="replace_memory", payload={"id": suggestion_id}, label=f"Replace [{replaces.entry_id}]"))
        actions.append(cl.Action(name="save_memory", payload={"id": suggestion_id}, label="Save as new" if replaces else "Save"))
        actions.append(cl.Action(name="dismiss_memory", payload={"id": suggestion_id}, label="Not now"))
        pending = cl.user_session.get("memory_suggestions") or {}
        pending[suggestion_id] = {"text": text.strip(), "category": decision.category, "actions": actions, "replaces": replaces}
        while len(pending) > _MAX_PENDING_SUGGESTIONS:
            pending.pop(next(iter(pending)))
        cl.user_session.set("memory_suggestions", pending)

        if replaces:
            body = (
                f"💾 **Update long-term memory?** (`{decision.category}`) This looks like a newer version of entry "
                f"[{replaces.entry_id}]:\n\n> **Saved now:** {strip_markdown_images(replaces.content)[:300]}\n\n"
                f"> **New:** {text.strip()}\n\n"
                "_Suggested locally by `nimble`. Nothing changes unless you click; \"Replace\" overwrites the old entry._"
            )
        elif decision.duplicate_of:
            # Offered, not swallowed: a wrong "this is already saved" would otherwise lose a statement silently.
            body = (
                f"💾 **Save to long-term memory?** (`{decision.category}`) Entry [{decision.duplicate_of.entry_id}] may "
                f"already say this: {strip_markdown_images(decision.duplicate_of.content)[:300]}\n\n> {text.strip()}\n\n"
                "_Suggested locally by `nimble`. Nothing is saved unless you click._"
            )
        else:
            body = (
                f"💾 **Save to long-term memory?** (`{decision.category}`)\n\n> {text.strip()}\n\n"
                "_Suggested locally by `nimble`. Nothing is saved unless you click._"
            )
        await cl.Message(content=body, author="Memory", actions=actions).send()
    except Exception:
        logger.exception("Memory suggestion failed (does not affect the answer)")


async def _take_memory_suggestion(action: cl.Action) -> dict | None:
    """Pops the suggestion a button belongs to (one use) and removes both of its buttons."""
    payload = action.payload if isinstance(action.payload, dict) else {}
    suggestion_id = payload.get("id")
    pending = cl.user_session.get("memory_suggestions") or {}
    item = pending.pop(suggestion_id, None) if isinstance(suggestion_id, str) else None
    for button in (item or {}).get("actions", [action]):
        try:
            await button.remove()
        except Exception:
            logger.debug("Could not remove a suggestion button", exc_info=True)
    return item


@cl.action_callback("save_memory")
async def on_save_memory(action: cl.Action):
    item = await _take_memory_suggestion(action)
    if item is None:
        await cl.Message(content="That suggestion is no longer available.", author="Memory").send()
        return
    result = await asyncio.to_thread(memory_proposals.save_confirmed, item["text"], item["category"])
    logger.info("Memory suggestion confirmed by the user: %s", result)
    await cl.Message(content=f"✅ {result}", author="Memory").send()


@cl.action_callback("replace_memory")
async def on_replace_memory(action: cl.Action):
    item = await _take_memory_suggestion(action)
    if item is None or item.get("replaces") is None:
        await cl.Message(content="That suggestion is no longer available.", author="Memory").send()
        return
    related = item["replaces"]
    result = await asyncio.to_thread(
        memory_proposals.replace_confirmed, related.entry_id, item["text"], item["category"], related.fingerprint
    )
    logger.info("Memory replacement confirmed by the user: %s", result)
    await cl.Message(content=f"✅ {result}", author="Memory").send()


@cl.action_callback("dismiss_memory")
async def on_dismiss_memory(action: cl.Action):
    await _take_memory_suggestion(action)


@cl.on_message
async def main(message: cl.Message):

    global _active_message_task
    _active_message_task = asyncio.current_task()

    conversation_start = time.time()

    steps = {}
    open_steps = {}
    tool_metrics = {}
    # One per user message (it holds partial state between tokens) — see core/image_guard.py.
    image_filter = MarkdownImageStreamFilter()
    # (label, start of the matched text) already reported to the user during this turn, so reading
    # several chunks of the same paper doesn't repeat the same notice.
    warned_injections: set[tuple[str, str]] = set()
    # True once the model itself saved something this turn: then no "save this?" suggestion is made
    # for the same message (it would duplicate the model's own entry).
    memory_written_by_model = False
    # For the reply check (core/output_check.py): did THIS turn run a tool that returns outside text, and
    # the model's reply exactly as generated — before the image filter, so an attempted leak is visible.
    turn_read_external = False
    raw_reply = ""
    # (tool name, result text) of the outside-text tools of this turn, for the second opinion on what they said
    # (core/external_check.py).
    turn_external_results: list[tuple[str, str]] = []
    pop_blocked_memory_writes()  # forget anything left over from an earlier turn
    conversation_metrics = {
        "llm_calls": 0,
        "tool_calls": 0,
        "tools_used": [],
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "llm_time": 0.0,
        "tool_time": 0.0
    }

    settings = cl.user_session.get("chat_settings")

    # With "Memory" on, Chainlit's own thread_id is reused (the same id
    # that identifies this conversation in the history sidebar): the
    # checkpointer automatically recovers the full history of previous
    # turns for this thread, only the new message needs to be sent — this
    # is also what makes resuming an old thread from the sidebar continue
    # the actual agent state, not just replay the transcript. With
    # "Memory" off, every message uses a new, isolated thread_id: the
    # agent sees nothing from previous turns.
    if settings.get("memory"):
        thread_id = cl.context.session.thread_id
    else:
        thread_id = str(uuid.uuid4())

    msg = cl.Message(author = "MV DATAWORKS", content="")
    await msg.send()

    # Ollama loads a model into memory on its first use in a while, which
    # can take a minute or more with zero visible progress otherwise —
    # easy to mistake for the app being frozen. This is removed the moment
    # real output starts (first tool call or first streamed token).
    loading_msg = cl.Message(
        author = "MV DATAWORKS",
        content = "⏳ Loading the model — this can take up to a minute the first time it's used in this session."
    )
    await loading_msg.send()
    loading_msg_cleared = False

    async def _clear_loading_message() -> None:
        nonlocal loading_msg_cleared
        if not loading_msg_cleared:
            loading_msg_cleared = True
            await loading_msg.remove()

    try:

        models_info = get_ollama_models_info()

        embedding_provider, embedding_model = _resolve_embedding_selection(
            settings.get("embedding_model")
        )

        # No chat-settings toggle for this — same auto-detect treatment as
        # arXiv tool availability. Picks the first vision-capable model
        # found (if any); with none installed (the common case), this is
        # just None and analyze_paper_figures never gets added.
        vision_model = next(
            (name for name, info in models_info.items() if info["is_vision"]),
            None
        )

        # The model's own limit, capped (see MAX_NUM_CTX in graph.py): a smaller model limit still wins, and still
        # triggers the warning below.
        num_ctx = min(models_info[settings["model"]]["context_length"], MAX_NUM_CTX)

        # Warned once per model per session, not on every message: the
        # message is informational, and repeating it each turn would bury
        # the actual conversation. Sent, not just logged — the user is the
        # one who can act on it (pick a model with a larger context).
        warned_models = cl.user_session.get("ctx_warned_models") or set()

        if num_ctx < MIN_RECOMMENDED_NUM_CTX and settings["model"] not in warned_models:
            warned_models.add(settings["model"])
            cl.user_session.set("ctx_warned_models", warned_models)
            logger.warning(
                "Model '%s' has num_ctx=%s, below the recommended minimum of %s",
                settings["model"], num_ctx, MIN_RECOMMENDED_NUM_CTX,
            )
            await cl.Message(
                author = "MV DATAWORKS",
                content = (
                    f"⚠️ **Context window too small.** '{settings['model']}' has a context "
                    f"length of {num_ctx:,} tokens. AInstein's system prompt, skills and tool "
                    f"definitions take roughly {MEASURED_PROMPT_TOKENS:,} tokens on their own, "
                    "and tool results (a paper search returns several thousand more) need room "
                    "on top of that. When the prompt doesn't fit, Ollama silently truncates it: "
                    "the model loses its tools and instructions, and answers will be wrong, "
                    "incomplete or invented. "
                    f"Please pick a model with a context length of at least "
                    f"{MIN_RECOMMENDED_NUM_CTX:,} tokens. With less than that, answers are not "
                    "supported and we can't take responsibility for poor results."
                )
            ).send()

        # Not yet a chat-settings toggle — see graph.py's build_agent for
        # why this defaults to False. Resolved as its own variable (rather
        # than relying on build_agent's own default) so the exact value
        # actually used for this turn is available below to log alongside
        # everything else in metrics.sqlite.
        reasoning = False

        agent = await build_agent(
            model_name = settings["model"],
            temperature = settings["temperature"],
            num_ctx = num_ctx,
            embedding_provider = embedding_provider,
            embedding_model = embedding_model,
            vision_model = vision_model,
            reasoning = reasoning
        )

        async for event in agent.astream_events(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message.content
                    }
                ]
            },
            # recursion_limit: deepagents' create_deep_agent() binds 9999 via
            # .with_config(...), but that default doesn't survive an explicit
            # config= passed at call time (verified live: without this, a
            # real turn hit LangGraph's raw default of 25 — and since
            # deepagents adds its own before_agent/after_model middleware
            # nodes (PatchToolCallsMiddleware, TodoListMiddleware) on top of
            # model/tools, one round of tool calls costs ~5 graph steps, not
            # 2 — so 25 was only ~5 rounds of real budget, not 25. 50 gives
            # ~10 rounds, enough for a multi-paper research turn without
            # being effectively unlimited.
            config={"configurable": {"thread_id": thread_id}, "recursion_limit": 50},
            version="v2"
        ):

            event_type = event["event"]

            # TRACK TOOL START
            if event_type == "on_tool_start":

                await _clear_loading_message()

                run_id = event["run_id"]

                tool_metrics[run_id] = {
                    "start_time": time.time()
                }

                tool_name = event["name"]

                step = cl.Step(name=f"🔧 {tool_name}")

                await step.__aenter__()

                input_raw = event["data"].get("input", {})

                # Display copy only — the model got the real arguments. Step panels render
                # markdown when expanded, so an image in here loads on a click on "Usado"
                # (verified live); see core/image_guard.py.
                step.input = strip_markdown_images(f"- Input:\n\n{input_raw}\n\n")

                steps[run_id] = step
                open_steps[run_id] = step

            # TRACK TOOL END
            elif event_type == "on_tool_end":

                run_id = event["run_id"]

                tool_name = event["name"]

                duration = (
                    time.time()
                    - tool_metrics[run_id]["start_time"]
                )

                output = event["data"].get("output")

                conversation_metrics["tool_calls"] += 1
                conversation_metrics["tool_time"] += duration
                conversation_metrics["tools_used"].append({
                    "tool": tool_name,
                    "duration": round(duration, 3),
                    "status": _extract_tool_status(output)
                })

                step = steps.get(run_id)

                # A memory tool that really ran and succeeded (a blocked call never gets here — see
                # pop_blocked_memory_writes in the end-of-turn code below).
                if tool_name in _MEMORY_WRITE_TOOLS:
                    try:
                        write_result = _format_tool_output(output)
                        if _extract_tool_status(output) == "success" and not write_result.startswith("Error"):
                            memory_written_by_model = True
                    except Exception:
                        logger.exception("Could not read a memory tool's result (does not affect the answer)")

                # Tell the person when external text looks like an order to the AI. The other
                # defenses neutralize it silently; this is the only place a human finds out.
                # A heuristic (see core/injection_detector.py) — it can fire on papers ABOUT
                # prompt injection, and the notice says so. Only for tools whose result is
                # third-party text, and only what wasn't already reported earlier this turn.
                if tool_name in _UNTRUSTED_CONTENT_TOOLS or tool_name in _UNTRUSTED_LABEL_TOOLS:
                    turn_read_external = True
                    try:
                        turn_external_results.append((tool_name, _format_tool_output(output)))
                    except Exception:
                        logger.exception("Could not keep a tool result for the external text check (does not affect the answer)")
                    try:
                        fresh = [
                            d for d in detect_injection(_format_tool_output(output))
                            if (d.label, d.snippet[:60]) not in warned_injections
                        ]
                        if fresh:
                            warned_injections.update((d.label, d.snippet[:60]) for d in fresh)
                            logger.warning(
                                "Possible prompt injection in the result of %s: %s",
                                tool_name, sorted({d.label for d in fresh}),
                            )
                            await cl.Message(content=format_notice(tool_name, fresh), author="Aviso de seguridad").send()
                    except Exception:
                        logger.exception("Injection notice failed (does not affect the answer)")

                if step:

                    output_raw = _format_tool_output(output)

                    # Display copy only, same reason as step.input above: tool results
                    # (paper text, search results) are untrusted, and the model still
                    # receives the real wrapped result — only what the browser renders
                    # is sanitized.
                    step.output = strip_markdown_images(
                        f"- Output:\n\n{output_raw}\n\n- Duration:\n\n{duration:.3f}s"
                    )

                    await step.__aexit__(None, None, None)
                    open_steps.pop(run_id, None)

            elif event_type == "on_chat_model_start":

                logger.debug("on_chat_model_start: %r", event)

            elif event_type == "on_chat_model_end":

                output = event["data"]["output"]

                metrics = extract_llm_metrics(event)

                logger.debug(
                    "on_chat_model_end content=%r tool_calls=%r metadata=%r",
                    output.content,
                    output.tool_calls,
                    output.response_metadata
                )

                conversation_metrics["llm_calls"] += 1

                conversation_metrics["input_tokens"] += metrics["input_tokens"]

                conversation_metrics["output_tokens"] += metrics["output_tokens"]

                conversation_metrics["total_tokens"] += metrics["total_tokens"]

                conversation_metrics["llm_time"] += metrics["duration"]

                # A model call ended: an image left open at the end of the stream is
                # replaced by the placeholder rather than released — the next model call
                # streams into the same message, and its first characters could otherwise
                # complete it on the client.
                tail = image_filter.flush()
                if tail:
                    await msg.stream_token(tail)

            elif event_type == "on_chat_model_stream":

                chunk = event["data"]["chunk"]

                if hasattr(chunk, "content") and chunk.content:

                    if isinstance(chunk.content, str):
                        raw_reply += chunk.content

                    # Tokens go to the browser as they are generated, INSIDE the model
                    # call — before OutputImageGuardrailMiddleware ever sees the finished
                    # message — and the client concatenates them, so an image is live the
                    # moment its closing ")" is emitted. Verified live: the middleware
                    # alone did not stop it. See core/image_guard.py.
                    safe = image_filter.feed(chunk.content)

                    if safe:
                        await _clear_loading_message()
                        await msg.stream_token(safe)

    except asyncio.CancelledError:

        # This session was superseded by a newer one (see
        # _cancel_previous_message_task) — nobody is watching this UI
        # anymore, just close whatever steps were left open and stop.
        for step in open_steps.values():
            try:
                await step.__aexit__(None, None, None)
            except Exception:
                logger.exception("Error closing an open step after cancellation")
        raise

    except Exception as exc:

        logger.exception("Error processing the user's message")

        await _clear_loading_message()

        for step in open_steps.values():
            try:
                await step.__aexit__(type(exc), exc, exc.__traceback__)
            except Exception:
                logger.exception("Error closing an open step after the failure")

        separator = "\n\n---\n" if msg.content else ""
        msg.content = f"{msg.content}{separator}⚠️ {_friendly_error_message(exc)}"
        await msg.update()
        return

    # End of the turn: release a held trailing "!" (see MarkdownImageStreamFilter.finish).
    tail = image_filter.finish()
    if tail:
        await msg.stream_token(tail)

    # The model tried to change long-term memory in a conversation that has read outside text and
    # MemoryWriteGuardMiddleware refused. Nothing was written; this is the only place the person
    # finds out that something attempted it.
    for blocked_tool in sorted(set(pop_blocked_memory_writes())):
        await cl.Message(
            content=(
                f"⚠️ **Memory change blocked.** The assistant tried to change long-term memory "
                f"(`{blocked_tool}`) in a conversation that has already read external text "
                "(papers or search results). Nothing was saved or deleted. If you did not ask "
                "for that, the text it read may have been trying to steer it."
            ),
            author="Security notice",
        ).send()

    conversation_metrics["execution_time"] = (
        time.time() - conversation_start
    )

    try:
        await log_turn(
            thread_id = thread_id,
            model = settings["model"],
            embedding_provider = embedding_provider,
            embedding_model = embedding_model,
            temperature = settings["temperature"],
            num_ctx = num_ctx,
            reasoning = reasoning,
            metrics = conversation_metrics
        )
    except Exception:
        logger.exception("Error saving observability metrics (does not affect the response)")

    df = pd.DataFrame(
        [
            {
                "Metric": "LLM Calls",
                "Value": conversation_metrics["llm_calls"]
            },
            {
                "Metric": "Tool Calls",
                "Value": conversation_metrics["tool_calls"]
            },
            {
                "Metric": "Input Tokens",
                "Value": conversation_metrics["input_tokens"]
            },
            {
                "Metric": "Output Tokens",
                "Value": conversation_metrics["output_tokens"]
            },
            {
                "Metric": "Total Tokens",
                "Value": conversation_metrics["total_tokens"]
            },
            {
                "Metric": "LLM Time (s)",
                "Value": round(
                    conversation_metrics["llm_time"],
                    2
                )
            },
            {
                "Metric": "Tool Time (s)",
                "Value": round(
                    conversation_metrics["tool_time"],
                    3
                )
            },
            {
                "Metric": "Execution Time (s)",
                "Value": round(
                    conversation_metrics["execution_time"],
                    2
                )
            }
        ]
    )

    elements = [
        cl.Dataframe(
            data=df,
            name="Session Metrics",
            display="side"
        )
    ]
    
    await cl.Message(
        content="📈 Session Metrics",
        elements=elements
    ).send()

    # Last, so it never delays the answer or the metrics above. The reply check comes first: it is the
    # safety one, and all of them use the same decision model, so the later calls find it already loaded.
    if turn_read_external:
        await _check_reply_for_steering(message.content, raw_reply)
        await _check_external_text(turn_external_results)
    await _offer_memory_suggestion(message.content, memory_written_by_model)
