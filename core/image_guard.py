"""Neutralizes markdown images (`![alt](url)`) in text the UI is about to display.

Why this exists as its own module (SECURITY_REVIEW.md finding #6): a markdown image
auto-loads in the browser the moment Chainlit renders it, so its URL is a silent channel
for sending data out. `.chainlit/config.toml`'s `unsafe_allow_html = false` doesn't stop it.

Three places display text that can carry one, and they need different handling:

* the model's final message  -> `OutputImageGuardrailMiddleware` (core/middleware.py) uses
  `strip_markdown_images` on the finished AIMessage. That alone turned out NOT to protect
  the real app (verified live, after step 4.2 had been marked done): `app.py` forwards each
  token to the browser as the model generates it, inside the model call and so before any
  middleware sees the finished message. The tokens accumulate on the client, and the image
  renders the instant its closing `)` arrives.
* the model's tokens as they stream -> `MarkdownImageStreamFilter` below, used by `app.py`.
* tool inputs/outputs shown in the step panels -> `app.py` runs `strip_markdown_images` on the
  display copy (the model still gets the real, wrapped tool result — only the UI copy changes).
"""

import re

# Deliberately simple, not catastrophic-backtracking-prone: alt text can't contain "]", the
# URL can't contain whitespace or parentheses. Reference-style images (`![alt][ref]`) are an
# accepted gap — the confirmed live exploit used plain inline syntax.
MARKDOWN_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(\s*[^()\s]+(?:\s+"[^"]*")?\s*\)')

# A proper prefix of something MARKDOWN_IMAGE_RE could still match once more text arrives.
# Used only by the stream filter, to know when it must hold text back instead of emitting it.
_IMAGE_PREFIX_RE = re.compile(r'!(?:\[[^\]]*(?:\](?:\(\s*(?:[^()\s]+(?:\s+"[^"]*"?)?\s*)?)?)?)?\Z')

BLOCKED_IMAGE_PLACEHOLDER = (
    "[blocked: an inline image reference was removed here for safety — a markdown image "
    "auto-loads the instant this message is displayed, which could silently leak data "
    "through its URL (SECURITY_REVIEW.md finding #6). The original URL isn't shown here "
    "either, since it could itself be untrusted.]"
)

# Longest a held-back candidate may grow before it's dropped. A real image tag is short; this
# only bounds the memory/latency cost of a model that opens `![` and never closes it.
_MAX_HELD_CHARS = 2000


def strip_markdown_images(text: str) -> str:
    return MARKDOWN_IMAGE_RE.sub(BLOCKED_IMAGE_PLACEHOLDER, text)


class MarkdownImageStreamFilter:
    """Sanitizes a token stream without letting an image through split across tokens.

    Tokens arrive in arbitrary pieces (`"!["`, `"ref](http://ev"`, `"il/x)"`), and the client
    concatenates whatever is emitted — so an image is dangerous the moment ITS LAST PIECE is
    emitted, even if no single token contained it. The rule is therefore: never emit text that
    could still turn into an image. Anything from a `!` onward that is a possible prefix of an
    image tag is held back until it either completes (replaced by the placeholder) or stops
    being a possible image (released as ordinary text). Only that candidate is delayed; the rest
    of the answer streams normally.

    Call `feed()` for each token, `flush()` when a model call ends and `finish()` when the whole
    turn ends. The next model call streams into the same message, so an image left open at the
    end of one call is replaced by the placeholder instead of emitted (a later token could
    otherwise complete it), and a bare trailing `!` is kept held across calls (the next call's
    `[a](url)` would complete it on the client) and only released by `finish()`.
    """

    def __init__(self) -> None:
        self._held = ""

    def feed(self, chunk: str) -> str:
        text = self._held + chunk
        self._held = ""
        out: list[str] = []

        while text:
            bang = text.find("!")
            if bang == -1:
                out.append(text)
                break

            out.append(text[:bang])
            text = text[bang:]

            full = MARKDOWN_IMAGE_RE.match(text)
            if full:
                out.append(BLOCKED_IMAGE_PLACEHOLDER)
                text = text[full.end():]
                continue

            if _IMAGE_PREFIX_RE.match(text):
                if len(text) > _MAX_HELD_CHARS:
                    out.append(BLOCKED_IMAGE_PLACEHOLDER)
                    text = ""
                else:
                    self._held = text
                    text = ""
                break

            # Not an image (e.g. "!important", "Wow!"): release just the "!" and keep scanning.
            out.append("!")
            text = text[1:]

        return "".join(out)

    def flush(self) -> str:
        """End of one model call. Only something that already reads `![` is an image in
        progress; a lone `!` isn't one yet, so it stays held for the next call."""
        if self._held.startswith("!["):
            self._held = ""
            return BLOCKED_IMAGE_PLACEHOLDER
        return ""

    def finish(self) -> str:
        """End of the whole turn: nothing more can arrive, so a held lone `!` is plain text."""
        held, self._held = self._held, ""
        return BLOCKED_IMAGE_PLACEHOLDER if held.startswith("![") else held
