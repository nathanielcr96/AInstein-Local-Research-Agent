# Messages used by EnsureFinalAnswerMiddleware (core/middleware.py) to
# force the turn to never end blank. NUDGE_MESSAGE is re-injected as a
# HumanMessage when the model responds empty with no tool_calls, both for
# the originally selected model and, on a second tier, for the fallback
# model. FALLBACK_MESSAGE replaces the content if the fallback model also
# ends up empty after its own retries. FALLBACK_MODEL_UNAVAILABLE_MESSAGE
# is used instead when the fallback model itself couldn't be called at all
# (e.g. not pulled in Ollama), so the user knows there's a missing model
# to install rather than just "the model wouldn't answer".
NUDGE_MESSAGE = (
    "You haven't written any message for the user this turn. "
    "Respond now in natural language summarizing the result for the "
    "user. Do not call any tool this turn."
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
