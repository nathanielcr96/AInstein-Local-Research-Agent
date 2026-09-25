---
name: challenge-conclusion
description: Stress-test a conclusion the user is leaning toward by actively looking for evidence AGAINST it in the papers already downloaded. Use when the user says things like "find evidence against", "play devil's advocate", "poke holes in this", "what could be wrong with my conclusion", "challenge my conclusion", "busca evidencia en contra", "abogado del diablo", "¿qué podría estar mal?", or states what they're leaning toward and asks what contradicts it. Not for summarizing one paper (paper-analysis) and not for deciding whether two papers disagree (compare-papers).
---

# Challenge a conclusion

The user has a conclusion they are leaning toward. Your job is the opposite of agreeing with it: find what in the papers actually cuts against it — and say so plainly when nothing does.

**Every tool below is a real tool call through your tool-calling mechanism. Never write a call out as text, a code block, or JSON — nothing runs that way and you get no data back.**

## Step 0 — get the conclusion (no tools yet)

Restate the user's conclusion in one line. If their message does not actually state a conclusion (only "play devil's advocate" with nothing to challenge), reply with a single question — "Which conclusion should I challenge? Give me one sentence." — and STOP. No tool calls, no guessing what they meant.

## Step 1 — aim at the opposite, not at a paraphrase

Turn the conclusion into at most 2 search queries aimed at where it could break: limitations, failure cases, negative or contradictory results, conditions where it does not hold. Example — conclusion "attention makes recurrent networks obsolete": search "recurrent models outperform attention on small data or long sequences" and "limitations of attention quadratic cost", NOT "attention is better than recurrent networks".

## Step 2 — search (real tool calls, at most 3 in total)

Call `search_paper_content` once per query. Leave `paper_id` out to sweep every downloaded paper, or pass it if the user named specific papers. You may add one `search_memory` call for notes the user already saved. Do not `read_paper` or `download_paper` here: the retrieved passages are the evidence, and only papers already downloaded are searched. These limits are enforced by the system, not just requested: a 4th `search_paper_content`, a 2nd `search_memory`, a repeat of an identical search, and every arXiv lookup tool (`search_papers`, `list_papers`, `get_abstract`, `citation_graph`, …) are rejected with an error. If you get that error, stop searching and write the answer from the results you already have.

**One `search_paper_content` call returns UP TO 5 papers' passages concatenated together, separated by `---` — read every one of them, not just the first.** Verified live to actually go wrong: a call returned 5 passages (papers X, Y, Z, W, V, in that order) and the model picked from the first two it saw (X and Z) while ignoring a passage from Y that appeared *twice across both calls* and was far more directly on-topic — the paper that shows up first, or most often near the top, is not necessarily the most relevant one. Before picking which passages to use as evidence, scan the full text of every call's result and judge each passage on ONE question only: does it specifically engage the conclusion's own claim (not just share a keyword or a broad topic with it)? A passage from a paper about a different application entirely (e.g. code generation, when the conclusion is about attention vs. recurrent networks) is weaker evidence than one that's actually arguing about the mechanism in question, even if the off-topic one happened to rank first in a result.

## Step 3 — copy this exact template and fill in only the placeholders

Verified live, twice, that a prose description of the required sections was not enough on its own: once the model answered as a "Paper A vs. Paper B" comparison table (that's `compare-papers`, a different skill), and once — even after being told not to do that — it answered as a per-paper summary ("Paper 1: Core Contribution / Key Findings / Limitations", "Paper 2: ..."), which is `paper-analysis`'s shape, not this one. Neither is acceptable, no matter how good its content is. To close that off, copy the literal template below and fill in only the `<...>` placeholders — do not rename, reorder, merge, or drop any heading, and do not organize the answer by paper instead of by evidence item:

```
**Conclusion under test:** <the one line from Step 0>

**Evidence against:**
- [<arXiv id>] <paper title>: "<verbatim quote copied character-for-character from a tool result this turn>" (paper states). <one sentence: how this specifically cuts against the conclusion> (interpretation).
- [<arXiv id>] <paper title>: "<verbatim quote>" (paper states). <one sentence> (interpretation).
(up to 3 items total; fewer if fewer than 3 real ones exist — see the Hard rules below for zero)

**Weak points of these objections:** <1-2 sentences> (interpretation).

**Coverage:** <the queries you ran>; <how many passages and how many distinct papers came back>.
```

## Hard rules

- Never invent a paper, an id, or a quote. If it was not in a tool result from this turn, it does not appear in the answer — not even as "as I recall".
- **Quotation marks mean verbatim text, and nothing else does.** Put something in quotation marks only when you copied it character-for-character from a tool result this turn. If you want to characterize or paraphrase what a paper investigates or argues, write it as your own words tagged **(interpretation)**, with no quotation marks — never invent a sentence (e.g. a "research question" you composed yourself) and present it in quotes as if the paper said it verbatim. Verified live to actually happen: an answer quoted two sentences framed as questions ("how can we make attention computationally efficient for streaming?") that do not appear anywhere in any tool result or in the paper — the model had composed them itself to summarize a paper's angle, then punctuated them as if they were the paper's own words.
- If nothing cuts against the conclusion, section 2 says exactly: "No evidence against found in the downloaded papers I searched", and Coverage says this reflects the limits of the local corpus, not that the conclusion is right. Do not pad with weak or tangential items to look thorough.
- Do not soften or end by agreeing with the conclusion. You may say which objection is strongest.
- A quote that merely mentions the topic is not evidence against; it has to argue, show, or measure something that conflicts with the conclusion.
- Between two retrieved passages, prefer the one that actually argues with the conclusion's specific mechanism over the one that's merely from a paper that ranked higher or was seen first — see Step 2 on reading every passage in a result, not just the first.
