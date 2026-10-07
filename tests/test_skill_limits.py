"""Tests for the skill trigger phrases, the per-skill tool-call limits and the global
ToolCallLimitMiddleware. Uses a SCRIPTED fake model: no Ollama, no GPU, no embeddings.

Run from the project root:  python tests/test_skill_limits.py
"""
import asyncio
import pathlib
import sys
import types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

import core.middleware as mw

FAILS = []


def check(name, cond, detail=""):
    print(("OK    " if cond else "FALLA ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)




# ---------------------------------------------------------------- trigger phrases
# Triggers are English only (AInstein is used in English): the Spanish phrasings were removed from the
# rules, so the cases below are English, and a Spanish message is checked NOT to match (see the end).
TRIGGER_CASES = [
    # (text, challenge, compare, graph)
    ("I lean toward thinking attention makes RNNs obsolete. Find evidence against that.", 1, 0, 0),
    ("Play devil's advocate on my conclusion that RLHF is unnecessary", 1, 0, 0),
    ("What could be wrong with this conclusion?", 1, 0, 0),
    ("Stress-test my view that attention is all you need.", 1, 0, 0),
    ("Find counterarguments to my claim that quantization never hurts accuracy.", 1, 0, 0),
    ("What contradicts my belief that bigger batches always help?", 1, 0, 0),
    ("Do 1706.03762 and 1707.06347 contradict each other?", 0, 1, 0),
    ("Do these two papers disagree about whether RL is needed?", 0, 1, 0),
    ("Compare these two papers: DPO and InstructGPT", 0, 1, 0),
    ("compare 2305.18290 and 2203.02155", 0, 1, 0),
    ("Are the results of 2305.18290 and 2203.02155 comparable?", 0, 1, 0),   # a dot inside an arXiv id is not a sentence end
    ("How do these two papers differ in their conclusions?", 0, 1, 0),
    ("Use the knowledge graph to tell me who wrote Attention Is All You Need", 0, 0, 1),
    ("Show me the co-authors of Ashish Vaswani.", 0, 0, 1),
    ("Which authors appear in more than one of the papers I've saved?", 0, 0, 1),
    ("What topics are connected to attention in my graph?", 0, 0, 1),
    # not triggers (traps)
    ("Quick summary of Attention Is All You Need", 0, 0, 0),
    ("Compare the prices of the GPUs", 0, 0, 0),
    ("Explain how LoRA works", 0, 0, 0),
    ("What are the arguments against raising the learning rate?", 0, 0, 0),
    ("What is the evidence that dropout helps?", 0, 0, 0),
    ("What contradicts that?", 1, 0, 0),                                   # a request for counter-evidence (challenge), NOT a comparison of two papers
    ("Some people say contradictory things about this.", 0, 0, 0),         # a bare 'contradict' no longer loads compare-papers
    ("Download both 1706.03762 and 1810.04805.", 0, 0, 0),                 # two ids, no comparison: compare would block download_paper
    ("Show me the citation graph of QLoRA.", 0, 0, 0),                     # the citation_graph tool, not the knowledge graph
    ("Summarize the paper on knowledge graph embeddings by Bordes.", 0, 0, 0),
    ("Tell me about graph neural networks.", 0, 0, 0),
    ("I have a collaborative filtering problem.", 0, 0, 0),
    # second round (phrasings a decision model recognised and the first rules missed) ...
    ("Which researchers appear in several of my saved papers?", 0, 0, 1),
    ("List the most connected authors.", 0, 0, 1),
    ("Find authors who worked together on more than one paper.", 0, 0, 1),
    ("Has Geoffrey Hinton written anything with Yann LeCun that I have saved?", 0, 0, 1),
    ("I believe RLHF is overrated. Argue against me.", 1, 0, 0),
    ("Can you tear apart my claim that LoRA never loses accuracy?", 1, 0, 0),
    ("What's the strongest case against my conclusion that PPO is obsolete?", 1, 0, 0),
    ("Where might I be wrong in thinking that BERT is dead?", 1, 0, 0),
    ("How do 2305.18290 and 2310.12036 differ in their assumptions?", 0, 1, 0),
    ("Do these two studies reach the same conclusion?", 0, 1, 0),
    ("Which of these two papers is right?", 0, 1, 0),
    # ... and the precision fixes: generic uses of the same words that must NOT load a skill
    ("What is a knowledge graph?", 0, 0, 0),
    ("Which authors should I follow on Twitter for ML news?", 0, 0, 0),
    ("How many co-authors does a typical ML paper have?", 0, 0, 0),
    ("Show the co-author order convention in physics papers.", 0, 0, 0),
    ("What does the graph in Figure 3 show?", 0, 0, 0),
    ("I think my model is overfitting. What could be wrong with my training code?", 0, 0, 0),   # debugging, not a conclusion to challenge
    ("Show me the arguments against deep learning for tabular data.", 0, 0, 0),                  # general information (a decision model took this for challenge at 0.81)
    ("How do transformers differ from RNNs?", 0, 0, 0),
    ("Do these two optimizers behave the same way?", 0, 0, 0),
    # Spanish phrasings no longer trigger anything
    ("Busca evidencia en contra de mi conclusión", 0, 0, 0),
    ("¿Se contradicen estos dos papers?", 0, 0, 0),
    ("Usa el grafo para decirme quién escribió Attention Is All You Need", 0, 0, 0),
]
for text, c, p, g in TRIGGER_CASES:
    got = (
        int(bool(mw._CHALLENGE_TRIGGER_RE.search(text))),
        int(bool(mw._COMPARE_TRIGGER_RE.search(text))),
        int(bool(mw._GRAPH_TRIGGER_RE.search(text))),
    )
    check(f"disparador {(c, p, g)}: {text[:60]}", got == (c, p, g), str(got))

# paper-analysis: forced on the literal words AND on the phrases the skill's own description lists
ANALYSIS_CASES = [
    ("Give me an extended analysis of arXiv 2305.14314", True),
    ("Analyze this paper for me: 1706.03762", True),
    ("Summarize arXiv 1706.03762 in one paragraph.", True),
    ("can u summarise the mamba paper?", True),
    ("Explain the paper 'Attention Is All You Need' to me.", True),
    ("Give me the TL;DR of the QLoRA paper.", True),
    ("tldr of 2305.14314", True),
    ("Is 2203.02155 worth reading?", True),
    ("What's your take on the DPO paper?", True),
    ("What does arXiv 2305.18290 actually say?", True),
    ("Break down the main contributions of this paper.", True),
    ("Walk me through the LoRA paper step by step.", True),
    ("I need a deep dive on the FlashAttention paper.", True),
    ("A standard summary of 1810.04805, please.", True),
    # not triggers: no paper, or a narrow factual question the skill excludes
    ("Summarize our conversation so far.", False),
    ("Explain how self-attention works.", False),
    ("Review my Python code for bugs.", False),
    ("What learning rate do they use in section 4?", False),
    ("How many parameters does the largest model in that paper have?", False),
    ("What does the paper say about rank?", False),                        # 'actually/really' is required, otherwise it is a narrow question
    ("What is the standard deviation of the reported accuracies?", False),
    ("Find me three recent papers about diffusion models.", False),
    ("Download arXiv 1706.03762.", False),
    ("What is the best way to write a literature review?", False),
    # second round: recognised by a decision model, missed by the first rules
    ("I'd like an overview of 'Attention Is All You Need' - what are its main ideas?", True),
    ("What are the key takeaways from arXiv 2106.09685?", True),
    ("What's the gist of 2307.08691?", True),
    ("Critique the QLoRA paper's experimental design.", True),
    ("Give me your honest opinion of the DPO paper.", True),
    ("Should I bother reading the FlashAttention paper?", True),
    ("I only have five minutes: is the RWKV paper any good?", True),
    ("Quick take on the Chinchilla paper?", True),
    ("Please review the paper on mixture-of-experts and tell me if the claims hold up.", True),
    ("Can you review 2205.14135 and tell me what is novel about it?", True),
    # precision: 'analyze'/'review' on something that is not a paper
    ("Analyze this CSV of GPU benchmark results.", False),
    ("Analyze the sentiment of this sentence: I love it.", False),
    ("Analyze my training logs and tell me why the loss spiked.", False),
    ("Review the paper submission guidelines for NeurIPS.", False),
    ("What is the review process for arXiv papers?", False),
    ("Review my Python code for bugs.", False),
    ("Our analyst will look at it tomorrow.", False),                       # 'analyst' (the job) is not 'analysis'
]
for text, expected in ANALYSIS_CASES:
    check(f"analisis {'fuerza' if expected else 'no fuerza'}: {text[:60]}", bool(mw._ANALYSIS_TRIGGER_RE.search(text)) == expected)


# ---------------------------------------------------------------- unit: _tool_call_rejection
def req(name, args, cid, messages):
    return types.SimpleNamespace(tool_call={"name": name, "args": args, "id": cid}, state={"messages": messages})


def ai(*calls):
    return AIMessage(content="", tool_calls=[{"name": n, "args": a, "id": i} for n, a, i in calls])


def ok(cid, name="search_paper_content"):
    return ToolMessage(content="passage", tool_call_id=cid, name=name)


def err(cid, name="search_paper_content"):
    return ToolMessage(content="boom", tool_call_id=cid, name=name, status="error")


mid = mw.ForceChallengeSkillMiddleware()
H = HumanMessage(content="I lean toward thinking X. Find evidence against that.")
plain = HumanMessage(content="Explain LoRA to me")

# a) non-triggering message: nothing is ever blocked, even arXiv tools
m = [plain, ai(("search_papers", {"q": "x"}, "a"))]
check("sin disparador no bloquea nada", mid._tool_call_rejection(req("search_papers", {"q": "x"}, "a", m)) is None)

# b) triggering message: arXiv lookup blocked (limit 0)
m = [H, ai(("search_papers", {"q": "x"}, "a"))]
check("arXiv bloqueado (limite 0)", "not available" in (mid._tool_call_rejection(req("search_papers", {"q": "x"}, "a", m)) or ""))

# c) 3 distinct searches ok, 4th blocked
m = [H, ai(("search_paper_content", {"q": "1"}, "1")), ok("1"), ai(("search_paper_content", {"q": "2"}, "2")), ok("2"),
     ai(("search_paper_content", {"q": "3"}, "3")), ok("3"), ai(("search_paper_content", {"q": "4"}, "4"))]
check("3a busqueda permitida", mid._tool_call_rejection(req("search_paper_content", {"q": "3"}, "3", m[:6])) is None)
check("4a busqueda bloqueada", "at most 3" in (mid._tool_call_rejection(req("search_paper_content", {"q": "4"}, "4", m)) or ""))

# d) exact duplicate of a successful call blocked; duplicate of a FAILED call allowed
m = [H, ai(("search_paper_content", {"q": "1"}, "1")), ok("1"), ai(("search_paper_content", {"q": "1"}, "2"))]
check("duplicado de llamada exitosa bloqueado", "exact" in (mid._tool_call_rejection(req("search_paper_content", {"q": "1"}, "2", m)) or ""))
m = [H, ai(("search_paper_content", {"q": "1"}, "1")), err("1"), ai(("search_paper_content", {"q": "1"}, "2"))]
check("reintento tras error permitido", mid._tool_call_rejection(req("search_paper_content", {"q": "1"}, "2", m)) is None)

# e) parallel calls in ONE AIMessage are numbered in order
m = [H, ai(*[("search_paper_content", {"q": str(i)}, str(i)) for i in range(5)])]
res = [mid._tool_call_rejection(req("search_paper_content", {"q": str(i)}, str(i), m)) is None for i in range(5)]
check("5 llamadas en paralelo: pasan 3 y se bloquean 2", res == [True, True, True, False, False], str(res))

# f) a new HumanMessage resets the count
m = [H, ai(*[("search_paper_content", {"q": str(i)}, str(i)) for i in range(3)]), ok("0"), ok("1"), ok("2"), HumanMessage(content="Once more: find evidence against Y"),
     ai(("search_paper_content", {"q": "z"}, "z"))]
check("mensaje nuevo reinicia el contador", mid._tool_call_rejection(req("search_paper_content", {"q": "z"}, "z", m)) is None)

# g) compare skill limits differ
cmp_ = mw.ForceCompareSkillMiddleware()
Hc = HumanMessage(content="Do the papers 1706.03762 and 1707.06347 contradict each other?")
m = [Hc, ai(*[("search_paper_content", {"q": str(i), "paper_id": "x"}, str(i)) for i in range(5)])]
res = [cmp_._tool_call_rejection(req("search_paper_content", {"q": str(i), "paper_id": "x"}, str(i), m)) is None for i in range(5)]
check("compare: pasan 4 y se bloquea 1", res == [True, True, True, True, False], str(res))


# ---------------------------------------------------------------- integration: scripted model through create_agent
class ScriptedModel(BaseChatModel):
    script: list = []
    pos: int = 0

    @property
    def _llm_type(self):
        return "scripted"

    def bind_tools(self, tools, **kw):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kw):
        msg = self.script[self.pos]
        self.pos += 1
        return ChatResult(generations=[ChatGeneration(message=msg)])


@tool
def search_paper_content(query: str) -> str:
    """stub"""
    return f"passage for {query}"


@tool
def search_papers(query: str) -> str:
    """stub"""
    return f"arxiv results for {query}"


@tool
def other_tool(x: str) -> str:
    """stub"""
    return f"other {x}"


def call(name, args, cid):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": cid}])


def tool_results(result, since_human_idx=0):
    return [(m.name, m.status, m.content[:40]) for m in result["messages"] if isinstance(m, ToolMessage)]


async def integration_skill():
    script = [
        call("search_paper_content", {"query": "q1"}, "c1"),
        call("search_paper_content", {"query": "q1"}, "c2"),  # exact duplicate
        call("search_paper_content", {"query": "q2"}, "c3"),
        call("search_paper_content", {"query": "q3"}, "c4"),  # 4th call to the tool -> over the limit of 3
        call("search_papers", {"query": "x"}, "c5"),          # arXiv tool -> off-limits
        AIMessage(content="respuesta final"),
    ]
    agent = create_agent(
        ScriptedModel(script=script), [search_paper_content, search_papers, other_tool],
        middleware=[mw.ForceChallengeSkillMiddleware(), ToolCallLimitMiddleware(run_limit=30, exit_behavior="continue")],
        checkpointer=InMemorySaver(),
    )
    cfg = {"configurable": {"thread_id": "t1"}}
    r = await agent.ainvoke({"messages": [HumanMessage(content="I lean toward thinking X. Find evidence against that.")]}, cfg)
    res = tool_results(r)
    for x in res: print("     ", x)
    check("skill: 5 resultados de tool", len(res) == 5, str(len(res)))
    check("skill: 1a ok", res[0][1] == "success")
    check("skill: 2a duplicada bloqueada", res[1][1] == "error" and "exact" in res[1][2] or "exact" in tool_results(r)[1][2] or res[1][1] == "error")
    check("skill: 3a ok", res[2][1] == "success")
    check("skill: 4a bloqueada por limite", res[3][1] == "error")
    check("skill: arXiv bloqueado", res[4][1] == "error")
    check("skill: el agente termina y responde", r["messages"][-1].content == "respuesta final")

    # same thread, next user message WITHOUT the trigger: skill limits off, and counters reset
    script2 = [call("search_papers", {"query": "y"}, "d1"), AIMessage(content="ok")]
    agent2 = create_agent(
        ScriptedModel(script=script2), [search_paper_content, search_papers, other_tool],
        middleware=[mw.ForceChallengeSkillMiddleware(), ToolCallLimitMiddleware(run_limit=30, exit_behavior="continue")],
        checkpointer=agent.checkpointer,
    )
    r2 = await agent2.ainvoke({"messages": [HumanMessage(content="Busca papers sobre LoRA")]}, cfg)
    last = [m for m in r2["messages"] if isinstance(m, ToolMessage)][-1]
    check("skill: mensaje sin disparador en el mismo hilo NO se bloquea", last.status == "success", f"{last.status} {last.content[:40]}")


async def integration_global():
    script = [call("other_tool", {"x": str(i)}, f"g{i}") for i in range(5)] + [AIMessage(content="fin")]
    agent = create_agent(
        ScriptedModel(script=script), [other_tool],
        middleware=[ToolCallLimitMiddleware(run_limit=3, exit_behavior="continue")], checkpointer=InMemorySaver(),
    )
    cfg = {"configurable": {"thread_id": "g1"}}
    r = await agent.ainvoke({"messages": [HumanMessage(content="hola")]}, cfg)
    res = tool_results(r)
    for x in res: print("     ", x)
    check("global: 3 pasan y 2 se bloquean", [s for _, s, _ in res] == ["success"] * 3 + ["error"] * 2, str(res))
    check("global: el agente termina", r["messages"][-1].content == "fin")

    script2 = [call("other_tool", {"x": "a"}, "h1"), call("other_tool", {"x": "b"}, "h2"), AIMessage(content="fin2")]
    agent2 = create_agent(ScriptedModel(script=script2), [other_tool],
                          middleware=[ToolCallLimitMiddleware(run_limit=3, exit_behavior="continue")], checkpointer=agent.checkpointer)
    r2 = await agent2.ainvoke({"messages": [HumanMessage(content="otra vez")]}, cfg)
    res2 = [(m.status) for m in r2["messages"] if isinstance(m, ToolMessage)][-2:]
    check("global: el contador por mensaje se REINICIA en el mensaje siguiente", res2 == ["success", "success"], str(res2))


async def main():
    print("--- integracion: skill ---")
    await integration_skill()
    print("--- integracion: limite global ---")
    await integration_global()
    print("\nFALLOS:", FAILS or "ninguno")


asyncio.run(main())
