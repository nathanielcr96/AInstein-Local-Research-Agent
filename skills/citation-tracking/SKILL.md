---
name: citation-tracking
description: How to explore a paper's citation network with citation_graph, and how to set up and check ongoing monitoring of a research topic with watch_topic and check_alerts. Use this whenever the user asks things like "what cites this paper", "what does this paper cite", "what's the related/follow-up work on this", "keep me updated on <topic>", "watch this topic for new papers", or "anything new on <topic> since last time".
---

# Citation tracking and topic monitoring

These three tools cover a different need than searching for a specific paper: following the research landscape *around* a paper or topic, either at a point in time (citations) or over time (monitoring).

## Exploring related work with `citation_graph`

`citation_graph(paper_id)` returns papers that cite, and are cited by, a given paper (via Semantic Scholar). Use it when the user wants to:
- Find related or follow-up work building on a paper they already have.
- Find the foundational work a paper is built on (its own references).
- Gauge how influential/established a paper is, by how much it's been cited.

The paper must already be identified by its arXiv id (via `search_papers`/`get_abstract` first if you don't have it yet) — this tool doesn't search by keyword itself, it only expands outward from a known paper.

**No matter how `citation_graph` turns out — success, rate-limited, or error — never follow it with `download_paper`, `read_paper`, `search_paper_content`, or `search_paper_text`.** This holds in both directions, and both have been verified live to actually happen and actually hurt:
- **On success**: `citation_graph`'s own JSON already contains everything needed — real titles, years, and authors for both directions (who cites this paper, what it cites) straight from Semantic Scholar's own record. Pulling the paper's full raw text on top of it (LaTeX, 90,000+ characters, hunting for `\citep{}` entries) dumps far more into context than one model call can hold alongside everything already gathered — the answer that followed cut off mid-sentence, and reconstructed a *worse*, partial bibliography from raw LaTeX instead of just using the structured data already in hand. If you have `citation_graph`'s result, that IS the complete answer — do not go looking for more.
- **On rate-limited/error**: reaching for the full paper text as a fallback is just as wrong, and was also observed live — after two failed `citation_graph` attempts, paginating through all ~97,000 characters of the paper via 8+ `read_paper` calls plus a `search_paper_text` sweep, still trying to reconstruct citations from informal in-text `\cite{}` keys (incomplete and far less reliable than a real bibliography), and the answer cut off mid-sentence again — same failure, same root cause, just reached from the other branch. **Say the failure plainly and stop there instead** — e.g. "Semantic Scholar rate-limited this request, so I couldn't retrieve QLoRA's citation graph; try again in a bit, or set `SEMANTIC_SCHOLAR_API_KEY` for a higher quota." Do **not** fall back to a plain `search_papers` keyword search either and present those results as if they were the citation graph — a keyword search for "QLoRA" returns papers *about* QLoRA, a completely different (and much noisier) thing from papers that actually *cite* QLoRA's Semantic Scholar record.

**Call `citation_graph` at most twice per question** — once plainly, and a second time only if you're deliberately changing something about the call (e.g. lowering `max_citations` because the first error said the payload was too large). Calling it again with the exact same arguments after a rate-limited response just burns more time against the same rate limit and delays reaching the "stop and report" step above.

**Pass a small `max_citations`, 10 by default — not the tool's max.** A well-cited paper can have thousands of citations, and even a "modest" `max_citations=50` returns *both* up to 50 citations and up to 50 references — 100 nested entries, tens of thousands of characters of JSON. That's too much to hold and synthesize in one go; it's the same overload that raw multi-page LaTeX causes elsewhere, and it's a likely cause if you find yourself unable to produce a real answer after a successful call. Only raise `max_citations` if the user explicitly wants a longer list, and consider it a sign to summarize (most-cited or most-recent highlights) rather than enumerate everything the response contains.

**The moment `citation_graph` returns `"status": "success"`, write your answer in that same message — do not stop, do not plan, do not produce a short or empty response "before" answering.** This is not optional politeness, it's the single most common way this tool fails in practice: after a successful call, it's easy to end the turn with something like "I don't see a result to summarize" or "how would you like me to help with this?" — even though the JSON you just received *is* the result and the user's question is right there above it. If you notice yourself about to write a sentence like either of those, stop — you have real data and a real question, use them instead of describing that you don't. There is nothing further to fetch and nothing to ask the user first.

Structure the answer directly from the returned JSON, in prose (not a raw dump of the JSON, and not one merged list — `citations` and `references` are two different directions and answer two different halves of the question, so keep them under two separate headings, even when one of them is short or empty):
1. One line on scale: how many citations found, how many references found (out of what was requested — note if you passed a smaller `max_citations` than exists in reality).
2. **Papers that cite this one** (from the `citations` field) — a few concrete highlights: title, and what's notable (topic overlap, recency). If everything returned shares an odd pattern (e.g. every citing paper is from the same very recent year), say so; it's worth flagging, not silently ignoring. If `citations` is empty, say so explicitly rather than omitting the section.
3. **Papers this one cites** (from the `references` field) — a few concrete highlights. These are usually the more immediately useful ones if the user asked "what should I look into next", since they're the foundational work this paper already built on.
4. If the user asked something like "anything relevant I should look into" — answer that as its own explicit step, by naming 1-2 *specific* papers from the two lists above (by title) and saying in one sentence why each is worth a look — not a generic closing offer to "look into anything you're interested in."

## Monitoring a topic with `watch_topic` and `check_alerts`

`watch_topic(topic, categories, max_results)` saves a persistent arXiv search — a standing definition of what "new" means for this topic, not a one-off search. Use it when the user wants to be kept updated on a research area going forward, not just get today's results.

`check_alerts(topic)` checks a previously saved watch for newly published papers since it was set up (or last checked). Call this to actually retrieve what's new — `watch_topic` alone doesn't surface results, it only registers the watch.

Typical flow: `watch_topic` once to set up monitoring for a topic the user cares about, then `check_alerts` whenever the user asks "anything new on X?" or at the start of a session if there's an active watch worth checking.

Same category-guessing caution as plain search applies to `watch_topic`'s `categories` parameter: leave it out unless the topic's field is already known, since arXiv spans far more than computer science.
