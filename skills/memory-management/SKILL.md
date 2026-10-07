---
name: memory-management
description: How to decide what belongs in long-term memory, when to add a new entry vs. correct an existing one, which category to use, and how to avoid saving unnecessary personal or identifying information. Use this whenever the user states a new research direction or goal ("estoy empezando a estudiar...", "quiero entender...", "I'm starting to look into...", "I want to understand how X works"), states a lasting preference for how you should behave ("a partir de ahora...", "prefiero que...", "from now on, always..."), explicitly asks you to remember something ("recuerda que...", "quiero que recuerdes...", "remember that..."), or when something you already have saved turns out to be wrong or outdated.
---

# Memory management

Long-term memory (`memory/store/long_term.md`) is not a transcript — it's a curated, structured record you build entry by entry with `update_memory`, `edit_memory`, and `search_memory`. Treat every write as a deliberate decision, not a reflex.

## Save the topic first, before you go do the work it implies

If the user's message states a new research direction, goal, or preference, call `update_memory` for it **right away** — before searching for papers, downloading anything, or doing other multi-step work the message also implies. A long detour of tool calls (searching, downloading, reading full paper content) can run long enough that you lose track of the fact you meant to save something, and the turn can end without it ever happening. Saving first costs one tool call and removes that risk entirely; saving "at the end, once the research part is done" does not reliably happen. There is now a second reason: as soon as a conversation reads a paper or search results, memory writes are blocked in it, so anything you meant to save has to be saved before that first read.

## Deciding what's worth saving

Save something only if it would actually change how you help in a *future* conversation: an active research topic, a standing preference about how the user wants you to behave, a keyword worth remembering, a paper's details, or a genuinely reusable note. Don't save things that are only relevant to the current turn (e.g. "the user just asked about X" isn't itself worth an entry unless X is now an ongoing research topic).

## Choosing a category

- `preference` — how the user wants you to behave, going forward.
- `research_topic` — an active line of research the user is pursuing.
- `keyword` — a term/concept worth resurfacing later.
- `paper` — details about a specific paper. Note: `download_paper`, `get_abstract`, and `read_paper` already record these automatically (via a middleware) every time you use them — you don't need to call `update_memory` yourself just because you looked at a paper. Do not try to add your own findings to a paper's entry afterwards: once a conversation has read paper text or search results, `update_memory` and `edit_memory` are blocked in it (the call returns an error and nothing is saved). Say the finding in your answer instead.
- `note` — anything else worth remembering that doesn't fit the above.

## Add vs. correct — don't create duplicates

Before calling `update_memory`, check your current memory index (shown in the system prompt) and, if there's any chance something related already exists, call `search_memory` first. If a matching entry exists, use `edit_memory` with its id to update/merge instead of creating a second, possibly contradictory entry. `update_memory` is for genuinely new information only.

## Don't save unnecessary personal or identifying information

Long-term memory persists indefinitely across sessions and is meant for *research continuity*, not a log of who said what. Before saving a `preference` or `note` entry:

- Do **not** record the user's or anyone else's personal details (full name, email, phone number, address, employer, etc.) unless the user explicitly asks you to remember it for a specific, stated reason.
- If personal information appears incidentally in a conversation (e.g. it was pasted in, or shown to you as context) and isn't itself the thing worth remembering, save the *substance* of what matters (the preference, the topic, the finding) and leave the identifying details out.
- This does **not** apply to `paper` entries — an author's name on a paper is bibliographic data, not personal data about the user, and is exactly what's needed to cite the paper correctly later. Keep authors, titles, and publication details as-is.

When in doubt, ask yourself: does remembering this specific detail help future research, or is it just incidental information that happened to pass through the conversation? Save the former, skip the latter.

## Searching before answering

Call `search_memory` whenever the current conversation might relate to something already saved — a topic the user has researched before, a stated preference, a paper they've looked at. It does a real semantic search (FAISS + reranker), not a literal text match, so phrase the query around the *meaning* of what you're looking for.
