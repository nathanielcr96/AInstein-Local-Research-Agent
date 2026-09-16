---
name: paper-analysis
description: Structured, depth-adjustable analysis of a specific paper — a quick 1-minute verdict on whether it's worth your time, a standard summary of what it says, or an extended analysis with related work and figures — always keeping a clear line between what the paper actually says and your own interpretation. Use this whenever the user asks things like "summarize this paper", "explain this paper to me", "give me a quick take / TL;DR", "is this worth reading / worth my time", "what's your take on this paper", "what does this paper actually say", or contains the word "analysis"/"analyze" anywhere in the message ("give me an analysis of X", "analyze this paper", "an extended analysis of...") no matter what else the message also asks for or how many papers it names — not when they're just searching for papers, or asking one narrow factual question search_paper_content can already answer directly.
---

# Paper analysis

This is about depth of *understanding*, not depth of *searching* — `search_paper_content` already answers narrow questions well ("what value does X occur at"). This skill is for when the user wants the paper actually explained to them, at a depth they choose (explicitly, or implied by how they asked).

Adapted from the public `paper-analyst` skill (flyer-li, MIT) and `paper-reader-heilmeier` (realzyzhang, MIT) — the depth-mode structure and the fact/interpretation labeling convention below both come from those, rewired onto this project's own tools and folded into one skill instead of two, and written from scratch rather than copied.

## The core rule: label every claim

Every substantive claim in your analysis gets one of two tags, inline or per-section — whichever reads more naturally:

- **(paper states)** — something the paper's own text actually says. If you're not looking directly at text that supports it, it doesn't get this tag.
- **(interpretation)** — your own inference, judgment, or synthesis: why something matters, how good the result really is, what's likely to break, how it compares to other work. This is where your actual value as an analyst shows up — don't be afraid to have a take — just don't let it masquerade as something the paper claimed.

This isn't optional formatting — it's the whole point of the skill. An analysis that silently blends the two is exactly the kind of quiet hallucination this exists to prevent, and it's the same instinct already applied elsewhere in this project (figure descriptions, citations) — the paper's text is a source to report on accurately, not something to blend with your own voice unmarked.

## Use the text a tool actually gives you

`get_abstract` puts the paper's text in its `abstract` field. `read_paper`/`search_paper_content` put theirs in `content`. That field is what you write from — read it and use it directly, the moment you have it.

## Pick a depth — ask if it's not obvious from how the user asked

**If the user's own message contains the word "quick", "standard", or "extended" (in any form — "an extended analysis", "just a quick take", "a standard summary"), that word IS the depth — use it directly, don't infer a different one from context.** Verified live to actually go wrong: a request for "an extended analysis of X, how it connects to Y and Z, plus anything worth remembering" — every part of that phrasing pointing at Extended — still got answered in Quick mode (a 5-bullet verdict, no related-work, no connection to Y or Z at all) because the depth got inferred from general vibe instead of matched to the literal word already in the message. Don't make this mistake: check for that word first, before reasoning about anything else.

**Quick** (~1 minute, Heilmeier-style triage — "does this paper matter for what I'm doing")

This mode is deliberately shallow and fast. Follow these constraints exactly:

- **Tools: call `get_abstract` and nothing else.** In this mode you do not call `read_paper`, `download_paper`, or `search_paper_content` — the abstract alone is the whole input. If you catch yourself wanting the full text, that means the user actually wants *Standard*, not *Quick* — switch modes rather than reading more.
- **Length: five bullet points, one sentence each. No section headings, no sub-bullets, no tables, no closing "verdict" paragraph beyond the last bullet.** If a bullet runs past one sentence, cut it.
- The five bullets, in order: (1) the problem being solved, (2) why it's hard / what prior approaches were missing, (3) what's actually new here, (4) who this matters to — tie it to the user's own research if `search_memory` shows one, (5) the single biggest risk or limitation, and end that last bullet with a plain yes/no/"only for X" on whether it's worth their time.
- **Still tag each bullet** with **(paper states)** or **(interpretation)** per the core rule above — the mode is shorter, not looser. Bullets 1–3 are usually (paper states) if they come straight from the abstract; bullets 4–5 and the worth-it call are usually (interpretation).

That's the entire output. It should take the reader under a minute. If you've written more than ~120 words you're in the wrong mode.

**Standard** (the default for "summarize this paper" / "what does this paper say")
The paper needs to be downloaded (`download_paper`) — if `list_papers` doesn't show it, download it once.
Then gather the content with **`search_paper_content`, not a full `read_paper`**: run it 3–5 times, once per thing you need to cover — the problem, the method, the key results, the acknowledged limitations. `search_paper_content` returns just the relevant passages, already cited; a full `read_paper` on a normal-length paper dumps tens of thousands of characters of raw LaTeX that is easy to get lost in. Only fall back to `read_paper` (with `return_full_text=true`, in a single call) if `search_paper_content` isn't available (no embedding model this session) or genuinely returns nothing useful across several queries.
Once you have the passages, **write the analysis** — do not keep reading. Cover: problem and approach, method (only as much technical detail as the user's question calls for), key results, the main contribution in one sentence, and limitations the paper itself acknowledges. This is the paper actually explained, not just triaged.

**Extended** (standard + how this paper fits into everything else)
Adds: related/prior work — use `citation_graph` for what the paper formally cites and is cited by, and `search_memory` for whether the user has already looked at connected papers or topics, so you can actually say how this connects to their own research rather than treating it in isolation. If there's a real finding worth remembering beyond the abstract (which is already auto-saved), use `edit_memory` on the paper's existing entry to add it — see the `memory-management` skill for how to do that without creating a duplicate or over-saving.

**Figures** (add to any mode above, when relevant)
If the user asks about a specific figure, diagram, or visual result — or a result is clearly better explained by a figure than by prose — call `analyze_paper_figures`. It's only available when a vision-capable model is configured; if it's not, say so plainly and work from the text alone rather than guessing at what a figure shows. Figure descriptions are themselves a model's interpretation of an image (see the tool's own docstring) — treat them as **(interpretation)**, not **(paper states)**, when you fold them into the analysis.

## When in doubt about depth

Default to **standard** — it's the one that actually answers "what does this paper say" without over- or under-delivering. Go **quick** only when the user is clearly deciding *whether* to look at a paper at all (skimming a list, triaging search results). Go **extended** when they're doing real research on a topic, not just checking one paper in isolation.
