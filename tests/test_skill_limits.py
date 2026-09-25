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
TRIGGER_CASES = [
    # (text, challenge, compare, graph)
    ("Me inclino a pensar que la atención hace obsoletas las RNN. Busca evidencia en contra.", 1, 0, 0),
    ("Hazme de abogado del diablo con mi conclusión sobre DPO", 1, 0, 0),
    ("Play devil's advocate on my conclusion that RLHF is unnecessary", 1, 0, 0),
    ("¿Qué podría estar mal en esta conclusión?", 1, 0, 0),
    ("¿Se contradicen 1706.03762 y 1707.06347?", 0, 1, 0),
    ("Do these two papers disagree about whether RL is needed?", 0, 1, 0),
    ("Compara estos dos papers: DPO e InstructGPT", 0, 1, 0),
    ("compare 2305.18290 and 2203.02155", 0, 1, 0),
    ("Usa el grafo para decirme quien escribio Attention Is All You Need", 0, 0, 1),
    ("Resumen rapido de Attention Is All You Need", 0, 0, 0),
    ("Compara los precios de las GPUs", 0, 0, 0),
    ("Explícame cómo funciona LoRA", 0, 0, 0),
    ("¿Qué hay en contra de subir el learning rate?", 0, 0, 0),
]
for text, c, p, g in TRIGGER_CASES:
    got = (
        int(bool(mw._CHALLENGE_TRIGGER_RE.search(text))),
        int(bool(mw._COMPARE_TRIGGER_RE.search(text))),
        int(bool(mw._GRAPH_TRIGGER_RE.search(text))),
    )
    check(f"disparador {(c, p, g)}: {text[:60]}", got == (c, p, g), str(got))


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
H = HumanMessage(content="Me inclino a pensar que X. Busca evidencia en contra.")
plain = HumanMessage(content="Explícame LoRA")

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
m = [H, ai(*[("search_paper_content", {"q": str(i)}, str(i)) for i in range(3)]), ok("0"), ok("1"), ok("2"), HumanMessage(content="Otra vez: busca evidencia en contra de Y"),
     ai(("search_paper_content", {"q": "z"}, "z"))]
check("mensaje nuevo reinicia el contador", mid._tool_call_rejection(req("search_paper_content", {"q": "z"}, "z", m)) is None)

# g) compare skill limits differ
cmp_ = mw.ForceCompareSkillMiddleware()
Hc = HumanMessage(content="¿Se contradicen los papers 1706.03762 y 1707.06347?")
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
    r = await agent.ainvoke({"messages": [HumanMessage(content="Me inclino a pensar que X. Busca evidencia en contra.")]}, cfg)
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
