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

Remember: Skills make you more capable and consistent. When in doubt, check if a skill exists for the task!"""
