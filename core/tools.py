from pathlib import Path

from langchain.tools import tool

# core/tools.py -> parent is core/, parent.parent is the project root,
# where skills/ lives (skills/ wasn't moved into core/, it's still user
# content, not support code).
SKILLS_DIR = (Path(__file__).parent.parent / "skills").resolve()

@tool
def read_skill(skill_name: str, file_name: str = "SKILL.md") -> str:
    """
    Reads the content of a file inside a skill.

    Can only read files inside the skills/<skill_name>/ folder, never
    outside it. Use this to load a skill's full instructions
    (file_name="SKILL.md" by default) or any supporting file it
    references (scripts, templates, etc.).
    """
    target = (SKILLS_DIR / skill_name / file_name).resolve()

    if SKILLS_DIR not in target.parents:
        return f"Error: '{skill_name}/{file_name}' is not a valid path inside skills/."

    if not target.is_file():
        return f"Error: file '{skill_name}/{file_name}' does not exist."

    return target.read_text(encoding="utf-8")
