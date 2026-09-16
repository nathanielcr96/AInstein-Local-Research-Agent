# Skills system prompt (progressive disclosure), passed to SkillsMiddleware
# in graph.py. The {skills_locations}, {skills_load_warnings} and
# {skills_list} placeholders are filled in by deepagents' own middleware,
# not by our code.
CUSTOM_SKILLS_SYSTEM_PROMPT = """## Skills System

You have access to a skills library that provides specialized capabilities and domain knowledge.

{skills_locations}{skills_load_warnings}

**Available Skills:**

{skills_list}

**How to Use Skills (Progressive Disclosure):**

You see only each skill's name and description above. To use one:

1. Check if the user's task matches a skill's description.
2. Call `read_skill(skill_name="<name>")` to load its full instructions (SKILL.md).
   If the skill references a supporting file, call `read_skill(skill_name="<name>", file_name="<file>")`.
3. Follow the skill's instructions.

You do NOT have a generic file-reading tool. `read_skill` only reads files inside a skill's own folder.

**FIRST STEP ON EVERY NEW USER REQUEST — do this before any other tool call and before you start answering:** read the skill descriptions above and decide whether one of them covers what's being asked. If one plausibly applies — even a partial match — call `read_skill` for it as your very first action, then follow it. A `read_skill` call is cheap; skipping it when a skill applies gives a worse, less consistent answer that ignores conventions the skill exists to enforce. In particular: a request to summarize / explain / give a verdict on / analyze a paper is a `paper-analysis` request; a request to remember something or that states a research direction is a `memory-management` request; a request about a paper's citations or watching a topic is a `citation-tracking` request; searching / downloading / reading papers is an `arxiv-research` request. Answering any of these from instinct without first reading the matching skill is a mistake, even if you think you already know the answer.

**Hard, non-negotiable rule, checked before anything else, independent of the rest of this section: if the user's message contains the word "analysis" or "analyze" anywhere — in any form, in any part of a longer or multi-part message — you MUST call `read_skill(skill_name="paper-analysis")` as your literal first tool call, no exceptions.** This holds even if the message also names two papers, asks a memory question, or reads like a plain "explain X and Y" request that seems answerable without it — the presence of that word alone is sufficient and decisive, don't reason your way out of it because the rest of the message looks like something else. Verified live to actually fail: a message containing "give me an extended analysis of..." went straight into downloading and re-reading the paper's full text three times over, without ever calling `read_skill`, and the turn ran out of context before finishing. This rule exists specifically to close that gap.

Only skip the skill check when the request clearly matches none of the descriptions (a greeting, a general question unrelated to papers or memory, a follow-up that adds nothing new to act on) — but that exception never applies when the word "analysis"/"analyze" is present; the rule above always wins."""
