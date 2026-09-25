# Messages used by EnsureFinalAnswerMiddleware (core/middleware.py) to
# force the turn to never end blank. NUDGE_MESSAGE_TEMPLATE is re-injected
# as a HumanMessage when the model responds empty (or with a canned
# deflection despite real tool data already present) with no tool_calls,
# both for the originally selected model and, on a second tier, for the
# fallback model. FALLBACK_MESSAGE replaces the content if the fallback
# model also ends up empty after its own retries. FALLBACK_MODEL_UNAVAILABLE_MESSAGE
# is used instead when the fallback model itself couldn't be called at all
# (e.g. not pulled in Ollama), so the user knows there's a missing model
# to install rather than just "the model wouldn't answer".
#
# Verified live (citation_graph deflection, points 8/9 of the memory-seeding
# test list): the older wording ("scroll back up: the user's most recent
# message above is the question...") asked qwen3.5:4b to do an implicit
# multi-hop search — find the real question among several tool-call/result
# pairs, and tell it apart from this very meta-instruction, which is itself
# injected as a HumanMessage. It failed that search 5/5 times, producing
# replies like "I don't see your most recent message in our conversation
# history" — i.e. it looked for a message and concluded there wasn't one,
# rather than using the one right above it. NUDGE_MESSAGE_TEMPLATE quotes
# the original question verbatim instead of describing where to find it, so
# there's nothing left to search for.
NUDGE_MESSAGE_TEMPLATE = (
    "You haven't answered yet this turn. Here is the exact question you "
    "still need to answer — quoted directly so you don't have to search "
    "for it:\n\n"
    "\"{question}\"\n\n"
    "The tool results already above in this conversation are real, "
    "successful data — not a failure, not a hypothetical. Use them "
    "directly to answer the quoted question now, in natural language. Do "
    "not call any tool this turn. Do not say you don't see a question or "
    "don't see a result — the quote above IS the question, and the data "
    "to answer it with is already above."
)

# Fallback wording for the rare case no HumanMessage can be found in the
# conversation to quote (kept so the middleware always has something to
# inject rather than failing to build a nudge at all).
NUDGE_MESSAGE = (
    "You haven't answered yet this turn. Scroll back up: the user's most "
    "recent message above is the question you still need to answer, and "
    "any tool results already in this conversation are the information "
    "to answer it with. Write that answer now, in natural language, "
    "using what you already have — do not call any tool this turn, and "
    "do not ask the user what they want; they already told you."
)

# Used instead of NUDGE_MESSAGE_TEMPLATE when _looks_like_textual_tool_call
# fires with NO tool result yet in the conversation (_has_tool_result is
# False) — i.e. the model described a tool call as text/code instead of
# ever actually calling one, so there's no data above to answer from yet.
# Verified live (graph_tools first-turn test): reusing NUDGE_MESSAGE_TEMPLATE
# here actively backfires — it tells the model "the tool results already
# above are real data... do not call any tool", which is false when nothing
# was ever called, and qwen3.5:4b then can't produce a real answer either
# (nothing to answer from) nor call the tool it needs (told not to),
# exhausting every retry and the fallback tier for nothing.
NUDGE_MESSAGE_CALL_TOOL_TEMPLATE = (
    "You did not actually answer or call a tool this turn — you wrote out "
    "what looks like a tool call as plain text (e.g. inside a code block "
    "or as pseudo-code) instead of issuing a real one, so nothing was "
    "executed and there is no data yet to answer from. Here is the exact "
    "question you still need to answer:\n\n"
    "\"{question}\"\n\n"
    "Make an actual tool call now — a real function call the system will "
    "execute — not text, code, or JSON describing one. Use the tool-calling "
    "mechanism itself, then wait for its real result before answering."
)

NUDGE_MESSAGE_CALL_TOOL = (
    "You did not actually answer or call a tool this turn — you wrote out "
    "what looks like a tool call as plain text instead of issuing a real "
    "one, so nothing was executed. Scroll back up for the user's most "
    "recent question, then make an actual tool call now — a real function "
    "call the system will execute, not text, code, or JSON describing one."
)

FALLBACK_MESSAGE = (
    "I wasn't able to generate a final answer after several attempts, "
    "even with the backup model. Please rephrase your question or try "
    "again."
)

FALLBACK_MODEL_UNAVAILABLE_MESSAGE = (
    "I wasn't able to generate a final answer with the selected model, "
    "and the backup model ('{model}') isn't available either — pull it "
    "with `ollama pull {model}` to enable this fallback tier. Please "
    "rephrase your question or try again."
)
