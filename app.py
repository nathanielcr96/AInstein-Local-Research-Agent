import sys
import asyncio
import chainlit as cl
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
from graph import build_agent
from core.ollama_functions import get_ollama_models_info, extract_llm_metrics
from core.huggingface_functions import get_huggingface_models_info
from core.chainlit_data import build_data_layer, authenticate_local_user
from observability.metrics_store import log_turn
import pandas as pd

logger = logging.getLogger(__name__)

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

@cl.on_message
async def main(message: cl.Message):

    global _active_message_task
    _active_message_task = asyncio.current_task()

    conversation_start = time.time()

    steps = {}
    open_steps = {}
    tool_metrics = {}
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

        agent = await build_agent(
            model_name = settings["model"],
            temperature = settings["temperature"],
            num_ctx = models_info[settings["model"]]["context_length"],
            embedding_provider = embedding_provider,
            embedding_model = embedding_model
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
            config={"configurable": {"thread_id": thread_id}},
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

                step.input = f"- Input:\n\n{input_raw}\n\n"

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

                conversation_metrics["tool_calls"] += 1
                conversation_metrics["tool_time"] += duration
                conversation_metrics["tools_used"].append({
                    "tool": tool_name,
                    "duration": round(duration, 3)
                })

                step = steps.get(run_id)

                if step:

                    output = event["data"].get("output")

                    output_raw = _format_tool_output(output)

                    step.output = f"- Output:\n\n{output_raw}\n\n- Duration:\n\n{duration:.3f}s"

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

            elif event_type == "on_chat_model_stream":

                chunk = event["data"]["chunk"]

                if hasattr(chunk, "content") and chunk.content:

                    await _clear_loading_message()
                    await msg.stream_token(chunk.content)

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
