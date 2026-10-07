"""Tests for the retry rules of EnsureFinalAnswerMiddleware (core/middleware.py `_needs_retry`).

A final reply that is empty, a tool call written as text, an announcement of more work ("Give me a second
to scan the appendix"), a permission request for what the user already asked, or a canned "how can I help?"
after tool results makes the agent try again. The opposite error costs more: a good answer that is retried
by mistake can end up replaced by the final apology. So half of these cases are legitimate replies that
contain the very phrases the rules look for.

The cases come from a study of 86 invented replies (scratch/turn_tagging_eval.py, labels written by Claude).
No model is needed.

Run with: python tests/test_final_answer_retry.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from core.middleware import _needs_retry

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        _FAILURES.append(label)


def retried(reply: str, had_tool_result: bool = True) -> bool:
    messages = [HumanMessage(content="question")]
    if had_tool_result:
        messages.append(ToolMessage(content="result", tool_call_id="c", name="search_papers"))
    return bool(_needs_retry(AIMessage(content=reply), messages))


# ---- replies that must be retried -------------------------------------------------------------------
SHOULD_RETRY = [
    # announcing work instead of doing it
    "Let me retrieve the next chunk of the paper before I give you the analysis.",
    "I'll continue reading the paper to get a complete picture before answering.",
    "First I need to read the rest of the paper.",
    "Before providing the analysis, let me fetch the remaining sections.",
    "Let me look at the results section and then summarize.",
    "One moment while I go through the rest of the document.",
    "I'm going to dig deeper into the methodology section first.",
    "Allow me to pull up the remaining pages.",
    "Give me a second to scan the appendix, then I'll answer.",
    "Next I will examine the experimental setup in detail.",
    "Bear with me while I pull the remaining sections.",
    "Hold on, I'm going to check the appendix before answering.",
    "Now I will review the ablation section.",
    "First I'll scan the related work, then I'll give you the answer.",
    "Let me fetch the rest of the text.",
    # a tool call written as text
    '```json\n{"tool_name": "read_paper", "args": {"paper_id": "1706.03762"}}\n```',
    'search_papers(query="diffusion models")',
    'I\'ll call the tool now: `get_abstract(paper_id="2106.09685")`',
    '{"task": "continue_reading_paper", "description": "read the next section"}',
    '<tool_call>{"name": "search_graph_nodes", "arguments": {"query": "Vaswani"}}</tool_call>',
    'Action: search_graph_nodes\nAction Input: {"query": "Attention Is All You Need"}',
    "Action: read_paper\nAction Input: 1706.03762",
    '```\nread_paper(paper_id="1706.03762")\n```',
    # real replies seen in use (English wording kept; the Spanish one is caught by the fenced call)
    'Para responder a tu pregunta, primero necesito encontrar el nodo.\n\nVoy a empezar buscando el paper:\n\n```\nsearch_graph_nodes(query="Attention Is All You Need")\n```',
    'I can help you with that. Here\'s the tool call:\n\n`search_paper_text(paper_id="arXiv:1606.04567", query="rlhf")`\n\nPlease wait for the result...',
    # asking permission to do what was asked
    "Would you like me to download the paper first?",
    "Before I proceed, can you confirm you want me to search arXiv?",
    "Should I go ahead and read the full text? Please confirm.",
    "I can look that up if you give me the go-ahead.",
    "Do you want me to use the knowledge graph for this?",
    "Could you confirm that you want me to download it?",
    "Do you want me to search the knowledge graph for this?",
    "Would you like me to read the full paper before I answer?",
    "Shall I go ahead and fetch the abstract? Let me know.",
    # empty
    "",
    "   \n  ",
]

for reply in SHOULD_RETRY:
    check(f"retried (with and without tool results): {reply[:70]!r}",
          retried(reply, had_tool_result=False) and retried(reply, had_tool_result=True))

# ---- deflections: only after tool results ---------------------------------------------------------------
DEFLECTIONS = [
    "I don't see a question in your message. How can I help?",
    "I see you've shared some results. What would you like me to do with them?",
    "This appears to be a new conversation. How can I help you today?",
    "What would you like me to summarize?",
    "Thanks for the information! Is there anything specific you'd like to know?",
    "I've received the search results. Let me know how you'd like to proceed.",
    "Great, I have the data now. What aspect should I focus on?",
    "Understood. Please tell me what you'd like me to do next.",
    "Is there anything specific you would like to know about these results?",
    "Got it. What would you like me to do with this information?",
    "I have the results now. How can I help?",
]

for reply in DEFLECTIONS:
    check(f"deflection retried after tool results: {reply[:60]!r}", retried(reply, had_tool_result=True))
    check(f"same text, no tool results, left alone: {reply[:60]!r}", not retried(reply, had_tool_result=False))

# ---- legitimate replies that must NOT be retried ----------------------------------------------------------
SHOULD_STAY = [
    "The paper introduces the Transformer, an architecture based entirely on self-attention. It reaches 28.4 BLEU on WMT 2014 English-to-German. Let me know if you want a deeper analysis.",
    # the stall phrases, inside real answers
    "Let me check the numbers: the baseline gets 26.0 BLEU and the proposed model 28.4, so the gain is 2.4 points.",
    "Before providing the list, note that the authors only discuss limitations briefly in Section 7. They mention training cost, the fixed context length and the lack of recurrence for very long sequences.",
    "If you want the details of the training setup, continue reading Section 3 of the paper, where they describe the optimizer and the schedule.",
    "The next chunk of the paper discusses the experimental setup: eight GPUs, a batch of 25,000 tokens, and 100,000 steps for the base model.",
    "I'll continue with the evaluation results: on English-to-French the big model reaches 41.8 BLEU, a new single-model record, at a quarter of the training cost.",
    "Let me check: the paper reports 91.2% on the test split and 88.5% on validation.",
    "Allow me to summarise: the method freezes the base model and trains small adapters, which cuts memory a lot.",
    "One moment of caution: the numbers come from the authors' own benchmark, so treat them as unverified.",
    "Before providing a verdict, I should say that the paper is a preprint and has not been peer reviewed. Overall it looks sound, with a clear ablation study and public code.",
    "I'm going to be direct: the evidence for the main claim is weak, since only one dataset is used.",
    "Hold on to the idea that the learning rate matters: the authors tuned it per model size, as Table 3 shows.",
    # offers that follow real content, or merely mention the words
    "The search found 4 papers. Would you like me to read any of them in full?",
    "Nothing matched your query in the graph. Would you like me to search arXiv instead?",
    "Nothing relevant: the search returned no results for that query. Would you like me to try different keywords?",
    "Yes, I can download it. Done: the paper 1706.03762 is now saved in your library.",
    "Done. Should you want the full text later, just ask.",
    "The authors' go-ahead for the second experiment was a pilot study with 12 users, reported in Section 6.",
    "I don't see the paper in your library, but it is on arXiv under 2203.02155 and I can download it for you.",
    "To read the paper in full, use the download tool first and then ask me about any section.",
    # a closing question after a real answer
    "Is there anything specific you'd like to know about the method? In short, it adds a low-rank update to each attention matrix, trains only that update, and merges it back at inference time, so there is no extra latency.",
    "Thanks for the question. The answer is no: the paper does not release its code.",
    # code and tool names inside answers
    "In LangChain you decorate a function with @tool and the agent calls it by name, for example search_papers(query=\"x\"). The result is passed back to the model as a message.",
    "Here is an example configuration:\n```json\n{\"lr\": 3e-4, \"epochs\": 3, \"batch_size\": 32}\n```\nThese are the values reported in Section 4.2.",
    # very short, polite, final
    "Yes.",
    "Sure, take your time. I'll read it as soon as you send it.",
    "Hello! How can I help with your research today?",
    "Hola, soy AInstein. ¿En qué puedo ayudarte con tus papers hoy?",
    # the project's own apology is final
    "I wasn't able to generate a final answer after several attempts, even with the backup model.",
]

for reply in SHOULD_STAY:
    # "Hello! How can I help" has no tool result in real use; check both situations except where a deflection is expected
    check(f"left alone (no tool results): {reply[:70]!r}", not retried(reply, had_tool_result=False))

# with tool results, these still must not be retried (none of them is a deflection)
STAY_WITH_TOOLS = [r for r in SHOULD_STAY if "How can I help" not in r and "ayudarte" not in r]
for reply in STAY_WITH_TOOLS:
    check(f"left alone (with tool results): {reply[:70]!r}", not retried(reply, had_tool_result=True))

# a reply with tool calls is never retried
check("a message that makes real tool calls is never retried",
      not _needs_retry(AIMessage(content="", tool_calls=[{"name": "search_papers", "args": {}, "id": "1"}]), [HumanMessage(content="q")]))

print()
if _FAILURES:
    print(f"{len(_FAILURES)} FAILED")
    sys.exit(1)
print("ALL PASSED")
