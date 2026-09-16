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
