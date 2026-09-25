---
name: compare-papers
description: Decide whether two papers genuinely disagree, or just asked different questions or used different setups. Use when the user asks "do these two papers disagree", "do they contradict each other", "are these results comparable", "compare paper X and paper Y", "¿se contradicen estos dos papers?", "¿discrepan?", "compara estos dos papers". Not for summarizing one paper (paper-analysis) and not for attacking a conclusion the user holds (challenge-conclusion).
---

# Compare two papers: real disagreement, or different questions?

Two papers that seem to conflict usually are not answering the same question, or not under the same conditions. Your job is to lay out what each paper actually asked and measured, and only then decide.

**Every tool below is a real tool call through your tool-calling mechanism. Never write a call out as text, a code block, or JSON — nothing runs that way and you get no data back.**

## Step 0 — identify the two papers

Get each paper's arXiv id from the user's message. If they gave a title, resolve it with `search_graph_nodes(query=<title>, node_type="paper")` (one call). If a paper is not in the graph or not downloaded, say which one is missing and STOP — do not compare from memory.

## Step 1 — retrieve what each paper says (real tool calls, at most 4 in total)

For each paper, call `search_paper_content(query="research question, experimental setup, datasets, evaluation metric, main result", paper_id=<its id>)` once. If a row of the table below is still empty for a paper after that, you may make ONE more targeted call for that paper — no more. These limits are enforced by the system, not just requested: a 5th `search_paper_content`, a 3rd `search_graph_nodes`, a repeat of an identical call, and every arXiv lookup tool (`search_papers`, `list_papers`, `get_abstract`, `citation_graph`, …) are rejected with an error. If you get that error, stop and write the answer from what you already have.

Even with `paper_id` set, one call can return more than one passage from that paper — read all of it, not just the first passage, before deciding a row is "not found."

## Step 2 — fill the table, copying this exact structure

Copy this literal template — same headings, same row order, one column per paper — and fill in only the `<...>` placeholders. Do not turn it into prose, do not rename or drop a row, do not organize the answer by paper instead of by row:

```
| | Paper A (<id>) | Paper B (<id>) |
|---|---|---|
| **Question asked** | <paper states> | <paper states> |
| **Setup** (data, scale, models, conditions) | <paper states> | <paper states> |
| **Metric** | <paper states> | <paper states> |
| **Main claim** | <paper states> | <paper states> |
```

Every cell is tagged **(paper states)**. If the retrieved text does not say it, write "not found in retrieved passages" — never fill a cell from memory or from what the paper is "known for". **A cell's content must be something the tool result actually says — put it in quotation marks only if it's copied character-for-character; otherwise state it in your own words with no quotation marks.** Never compose a sentence yourself (e.g. a "research question" summarizing the paper's angle) and present it in quotes as if the paper stated it verbatim — that's exactly as wrong here as inventing a quote for a paper's claim.

## Step 3 — verdict: exactly one of these four, using this exact structure

```
**Verdict: <Genuine disagreement | Different questions | Different conditions | Can't tell>**

<1 sentence tagged (interpretation): which table rows decide it>

**What would settle it:** <1 sentence tagged (interpretation)>
```

- **Genuine disagreement** — same question, comparable setup and metric, incompatible claims.
- **Different questions** — the papers ask different things, so their claims do not compete.
- **Different conditions** — same question, but different data, scale, metric, or setup, so the results are not comparable as they stand.
- **Can't tell** — a decisive row is "not found" for at least one paper.

## Hard rules

- The verdict must follow from the table. "Genuine disagreement" is allowed only when Question, Setup, and Metric are all filled in for BOTH papers.
- Different headline numbers are not a disagreement. Most apparent conflicts are different questions or different conditions — lean that way unless the table forces otherwise.
- Never invent a paper, an id, a number, or a quote. If it was not in a tool result from this turn, it does not appear in the answer.
- Quotation marks mean verbatim text, copied character-for-character from a tool result this turn, and nothing else — see Step 2.
