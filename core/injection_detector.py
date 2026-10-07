"""Heuristic detector for text that looks like an instruction aimed at the AI reading it.

Purpose (SECURITY_REVIEW.md, guardrails): the other defenses NEUTRALIZE an injection — the
untrusted-content wrapper, the image guard, the tool limits — but they are silent: nothing tells
the person at the keyboard that a paper they asked about just tried to give their assistant orders.
`app.py` uses this on every tool result that carries external text and shows a short notice.

This is a SMELL detector, not a security boundary, and it is deliberately tuned for few false alarms
over catching everything:
  * it can be evaded (paraphrase, other languages, encoding) — a paper that gets past it is still
    handled by the defenses that don't depend on recognizing the text, and `core/external_check.py`
    gives the passages it lets through a second opinion with a decision model;
  * it WILL fire on papers ABOUT prompt injection, which quote exactly these phrases as examples —
    the notice says so, and shows the matched text so the reader can judge for themselves;
  * patterns are phrase-shaped, never single words ("dan", "assistant", "you are" alone would match
    ordinary prose, names and every tutorial).

Measured against the 169 real arXiv papers in this repo when it was written — see
tests/test_injection_detector.py for the numbers it is pinned to.
"""

import json
import re
from dataclasses import dataclass

# (label, human description, regex). Matched against lower-cased text with whitespace collapsed.
_RULES: list[tuple[str, str, str]] = [
    (
        "override",
        "asks to ignore or replace earlier instructions",
        r"\b(?:ignore|disregard|forget|override|bypass)\s+(?:all\s+|any\s+|of\s+|the\s+|your\s+|these\s+|those\s+)*"
        r"(?:previous|prior|above|earlier|preceding|original|system|initial)\s+"
        r"(?:instructions?|prompts?|rules?|guidelines?|directions?|context|configuration)"
        r"|\bsystem\s+override\b"
        r"|\b(?:new|updated|overriding)\s+instructions?\s+(?:for|to)\s+the\s+(?:assistant|ai|model|llm)\b"
        r"|\bsupersed(?:e|es|ing)\s+(?:all\s+|any\s+|every\s+)?(?:prior|previous|earlier)\s+(?:instructions?|configuration|rules)"
        r"|\bsuperse?ding\s+all\s+prior\s+configuration\b",
    ),
    (
        "addresses the AI",
        "speaks directly to an AI assistant reading the document",
        # "instructions to/for the LLM" is deliberately NOT here: LLM-prompting papers say it all
        # the time ("a proper instruction for LLM prompting" flagged a real paper).
        r"\b(?:note|message|notice|attention)\s+(?:to|for)\s+(?:the\s+)?(?:ai|a\.i\.|llm|language\s+model|assistants?|agents?|memory\s+systems?|automated)"
        r"(?:\s+(?:and|or|,)\s+\w+(?:\s+\w+)?)?"
        r"|\b(?:ai|llm)\s+assistants?\s+(?:reading|processing|summari[sz]ing|analy[sz]ing)\b"
        r"|\bassistant\s*[,:-]?\s*(?:action\s+required|you\s+(?:must|should|need\s+to|will)\s+now)\b"
        r"|\breviewer-visible\s+metadata\b.{0,40}\bassistant\b"
        r"|\bto\s+any\s+(?:ai|llm|language\s+model)\s+(?:reading|summari[sz]ing|processing)\b",
    ),
    (
        "role hijack",
        "tries to change the assistant's role or remove its restrictions",
        r"\byou\s+are\s+no\s+longer\s+(?:a\s+|an\s+|the\s+|bound\b)"
        r"|\bdo\s+anything\s+now\b"
        r"|\bdan\s+mode\b|\bdeveloper\s+mode\s+(?:enabled|activated|on)\b"
        r"|\bjailbreak(?:ing|ed)?\s+(?:prompt|mode)\b"
        r"|\b(?:without|ignoring)\s+(?:any\s+|your\s+|all\s+)?(?:normal\s+)?(?:safety|content)\s+(?:guidelines|restrictions|policies)\b",
    ),
    (
        "concealment",
        "asks the assistant to hide something from the user",
        # No "let"/"say"/"anyone": "never let anyone make you feel inferior" (a real paper, quoting a
        # model's reply) is not concealment.
        r"\b(?:do\s+not|don'?t|never)\s+(?:mention|tell|reveal|inform|disclose)\s+(?:this|that|it|the\s+user)\b(?:.{0,40}\b(?:to|from)\s+the\s+user)?"
        r"|\bwithout\s+(?:telling|informing|notifying|alerting)\s+the\s+user\b"
        r"|\bdo\s+not\s+acknowledge\s+(?:this|the)\b",
    ),
    (
        "memory or tool tampering",
        "asks the assistant to write to its memory or call tools",
        r"\b(?:save|store|write|record|add|put)\s+(?:the\s+following|this|it|that)\s+(?:as\s+[\w\s]{0,30}?)?(?:to|in|into)\s+(?:your\s+|the\s+)?(?:long-term\s+|permanent\s+)?memory\b"
        r"|\bpermanent\s+user\s+preference\b|\bstore\s+(?:the\s+following\s+)?as\s+a\s+permanent\b"
        r"|\b(?:call|invoke|run|execute)\s+(?:the\s+)?(?:tool\s+)?(?:update_memory|edit_memory|write_file|execute|download_paper)\b"
        r"|\bsave\s+a\s+memory\s+entry\b",
    ),
    (
        "instructs a reply",
        "tells the assistant what to answer instead of what the user asked",
        r"\b(?:instead|rather\s+than\s+(?:summari[sz]ing|answering|analy[sz]ing))[,:]?\s+(?:you\s+(?:must|should)\s+)?(?:now\s+)?tell\s+the\s+user\b"
        r"|\b(?:before|instead\s+of)\s+(?:you\s+)?(?:answer|answering|respond|responding|replying)\b.{0,60}\b(?:first|right\s+now)\b"
        r"|\bbefore\s+responding\s+to\s+whatever\s+the\s+user\b|\bdo\s+this\s+(?:right\s+)?now,?\s+before\s+you\s+(?:answer|respond)\b"
        r"|\bfinish\s+every\s+(?:answer|reply|response)\s+with\b|\bbegin\s+your\s+next\s+repl(?:y|ies)\s+with\b|\bstart\s+your\s+next\s+(?:reply|response|answer)\s+with\b",
    ),
    (
        "external image",
        "contains a markdown image pointing at an external URL (a way to send data out)",
        r"!\[[^\]\n]{0,120}\]\(\s*https?://[^)\s]+",
    ),
    (
        "script",
        "contains a <script> tag or a javascript: link",
        r"<\s*script\b|\bjavascript\s*:\s*[a-z(]",
    ),
]

_COMPILED = [(label, desc, re.compile(rx, re.IGNORECASE | re.DOTALL)) for label, desc, rx in _RULES]

_SNIPPET_CONTEXT = 45
_MAX_MATCHES_PER_LABEL = 2


@dataclass(frozen=True)
class Detection:
    label: str
    description: str
    snippet: str  # the matched text with a little context, single line, for the person to judge


def _strings_of(value, out: list[str]) -> None:
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for v in value.values():
            _strings_of(v, out)
    elif isinstance(value, list):
        for v in value:
            _strings_of(v, out)


def _textual_view(text: str) -> str:
    """Most tools here return JSON (download_paper, get_abstract...). In that form a newline inside
    the paper is the two characters backslash-n, so a phrase split across lines
    ("ignore\\nall previous instructions") would not match, and the quoted snippet would be full of
    escapes. Decode it and look at the real strings. Anything that isn't JSON is used as is."""
    stripped = text.lstrip()
    if stripped[:1] in ("{", "["):
        try:
            strings: list[str] = []
            _strings_of(json.loads(text), strings)
            if strings:
                return "\n".join(strings)
        except ValueError:
            pass
    return text


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", _textual_view(text))


def detect_injection(text: str) -> list[Detection]:
    """Returns one Detection per distinct (label, matched text) found — at most a couple per label.

    Empty list means nothing suspicious *by these patterns*, not that the text is safe.
    """
    if not text:
        return []
    flat = _normalize(text)
    found: list[Detection] = []
    for label, desc, rx in _COMPILED:
        seen: set[str] = set()
        for m in rx.finditer(flat):
            key = m.group(0).lower()[:80]
            if key in seen:
                continue
            seen.add(key)
            start = max(0, m.start() - _SNIPPET_CONTEXT)
            end = min(len(flat), m.end() + _SNIPPET_CONTEXT)
            snippet = ("…" if start else "") + flat[start:end].strip() + ("…" if end < len(flat) else "")
            found.append(Detection(label, desc, snippet))
            if len(seen) >= _MAX_MATCHES_PER_LABEL:
                break
    return found


def format_notice(tool_name: str, detections: list[Detection]) -> str:
    """The message shown to the user (Spanish, like the rest of the UI copy the user reads)."""
    lines = [
        f"⚠️ **Posible instrucción oculta en el resultado de `{tool_name}`.** "
        "El texto de un paper parece dirigirse a la IA que lo lee. "
        "El agente lo trata como datos, no como órdenes, pero conviene que lo sepas:",
        "",
    ]
    for d in detections:
        lines.append(f"- *{d.description}* — «{d.snippet[:220]}»")
    lines += [
        "",
        "_Puede ser una falsa alarma: los papers sobre inyección de prompts citan estas frases como ejemplo._",
    ]
    return "\n".join(lines)
