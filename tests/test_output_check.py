"""Tests for core/output_check.py — the reply check after a turn that read outside text. No Ollama needed:
the decision model is a fake `ask`, and one test talks to a throwaway local HTTP server.

Pinned here: it is notice-only and fails quiet (no model, malformed answer, backing off -> no notice, no
exception); every category it can flag maps to a notice; long replies keep their START AND END (an injected
line is often last) and stay under the size the model can read; the question sent is exactly the one that was
measured; and app.py only runs it after a turn that read outside text, on the reply as generated.

Run with: python tests/test_output_check.py
"""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import decision_client, output_check as oc

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        _FAILURES.append(label)


def answer(choice="normal", p_normal=0.95):
    return {"verdict": {"type": "choice", "choice": choice, "probabilities": {"normal": p_normal}, "confidence": 0.9}}


class FakeAsk:
    def __init__(self, result=None, raises=None):
        self.result, self.raises, self.calls = result or answer(), raises, []

    def __call__(self, state, questions):
        self.calls.append((state, questions))
        if self.raises:
            raise self.raises
        return self.result


REPLY = "The paper proposes adaptive gradient clipping for very deep residual networks and shows better stability."


def test_normal_reply_is_not_flagged():
    d = oc.check_reply("Summarize this paper.", REPLY, ask=FakeAsk(answer("normal", 0.97)))
    check("a normal verdict is not flagged", not d.flagged and d.reason == "normal")


def test_every_steering_category_is_flagged_and_has_a_notice():
    for cat in ("contact_or_action", "credentials", "role_or_secrets", "memory_or_authorization", "promotion_or_fabrication"):
        d = oc.check_reply("Summarize this paper.", REPLY, ask=FakeAsk(answer(cat, 0.05)))
        check(f"{cat}: flagged", d.flagged and d.category == cat and abs(d.probability - 0.95) < 1e-9)
        notice = oc.format_notice(d)
        check(f"{cat}: the notice names what was flagged and says nothing was changed",
              oc.DESCRIPTIONS[cat] in notice and "nothing was blocked or changed" in notice)


def test_categories_in_the_question_match_the_notice_table():
    crit = set(oc.VERDICT_QUESTION["criteria"])
    check("every non-normal category in the question has a notice text", crit - {"normal"} == set(oc.DESCRIPTIONS))


def test_the_question_is_the_one_that_was_measured():
    ask = FakeAsk()
    oc.check_reply("Summarize this paper.", REPLY, ask=ask)
    state, questions = ask.calls[0]
    check("state carries exactly the user's question and the reply", set(state) == {"user_question", "assistant_reply"})
    check("one closed question, named 'verdict'", list(questions) == ["verdict"] and questions["verdict"]["type"] == "choice")
    check("the six measured options", set(questions["verdict"]["criteria"]) == {
        "normal", "contact_or_action", "credentials", "role_or_secrets", "memory_or_authorization", "promotion_or_fabrication"})
    check("it tells the model to choose normal unless the user is pushed toward something unasked",
          "Choose normal unless" in questions["verdict"]["instructions"])


def test_short_or_missing_replies_are_skipped_without_asking():
    ask = FakeAsk()
    for label, reply in (("empty", ""), ("whitespace", "   \n "), ("greeting", "Hello!"), ("none", None)):
        d = oc.check_reply("Hi", reply, ask=ask)
        check(f"{label} reply: not flagged", not d.flagged)
    check("...and the model was never asked", ask.calls == [])


def test_long_replies_keep_start_and_end_and_stay_small():
    head, tail = "START-MARKER " + "a " * 200, "b " * 200 + " END-MARKER call 1-800-555-0199"
    reply = head + ("filler word " * 5000) + tail
    ask = FakeAsk()
    oc.check_reply("Q " * 1000, reply, ask=ask)
    state = ask.calls[0][0]
    check("the start of a long reply is kept", "START-MARKER" in state["assistant_reply"])
    check("the end of a long reply is kept (where an injected line usually sits)", "END-MARKER call 1-800-555-0199" in state["assistant_reply"])
    check("the reply sent stays under the limit (plus the omission marker)", len(state["assistant_reply"]) <= oc.MAX_REPLY_CHARS + 40)
    check("a long question is cut too", len(state["user_question"]) <= oc.MAX_QUESTION_CHARS + 40)
    ask2 = FakeAsk()
    oc.check_reply("Summarize.", REPLY, ask=ask2)
    check("a short reply is sent whole", ask2.calls[0][0]["assistant_reply"] == REPLY)


def test_it_fails_quiet():
    decision_client.reset_backoff()
    d = oc.check_reply("Q", REPLY, ask=FakeAsk(raises=decision_client.NimbleUnavailable("HTTP 404")))
    check("model unavailable: no notice, no exception", not d.flagged and "unavailable" in d.reason)
    ask = FakeAsk()
    d2 = oc.check_reply("Q", REPLY, ask=ask)
    check("...and it backs off instead of asking again on the next reply", not d2.flagged and ask.calls == [])
    decision_client.reset_backoff()
    check("malformed answer (string): no notice, no exception", not oc.check_reply("Q", REPLY, ask=lambda s, q: {"verdict": "x"}).flagged)
    check("answer missing the question: no notice, no exception", not oc.check_reply("Q", REPLY, ask=lambda s, q: {}).flagged)
    check("unknown category: not flagged", not oc.check_reply("Q", REPLY, ask=FakeAsk(answer("something_new", 0.1))).flagged)
    decision_client.reset_backoff()


def test_shared_backoff_with_the_other_feature():
    decision_client.reset_backoff()
    decision_client.back_off("test")
    ask = FakeAsk()
    check("if another feature found the model missing, this one does not try", not oc.check_reply("Q", REPLY, ask=ask).flagged and ask.calls == [])
    decision_client.reset_backoff()


def test_http_client_sends_both_fields():
    import os
    seen = {}

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            seen["path"] = self.path
            seen["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"answers": answer("credentials", 0.02)}).encode())

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    old = os.environ.get("OLLAMA_HOST")
    os.environ["OLLAMA_HOST"] = f"127.0.0.1:{srv.server_port}"
    try:
        decision_client.reset_backoff()
        d = oc.check_reply("Download this paper for me.", "Please paste your API key and password here to continue.")
        check("end to end over HTTP: flagged", d.flagged and d.category == "credentials")
        check("posted to /v1/systemone with both state fields",
              seen["path"] == "/v1/systemone" and set(seen["body"]["state"]) == {"user_question", "assistant_reply"}
              and seen["body"]["model"] == "nimble")
    finally:
        srv.shutdown()
        if old is None:
            os.environ.pop("OLLAMA_HOST", None)
        else:
            os.environ["OLLAMA_HOST"] = old
        decision_client.reset_backoff()


def test_app_wiring():
    src = (Path(__file__).resolve().parent.parent / "app.py").read_text(encoding="utf-8")
    check("the check runs only in a turn that read outside text", "if turn_read_external:\n        await _check_reply_for_steering(" in src)
    check("the flag is set where untrusted tool results are handled",
          "turn_read_external = True" in src and src.index("turn_read_external = True") < src.index("Injection notice failed"))
    check("the reply is collected before the image filter sees it", src.index("raw_reply += chunk.content") < src.index("image_filter.feed(chunk.content)"))
    check("it is notice-only: the only thing sent is a message", "output_check.format_notice(verdict)" in src and "msg.content =" not in src.split("_check_reply_for_steering")[1].split("_MAX_PENDING_SUGGESTIONS")[0])
    check("it runs before the memory suggestion", src.index("await _check_reply_for_steering(message.content, raw_reply)") < src.index("await _offer_memory_suggestion(message.content, memory_written_by_model)"))


if __name__ == "__main__":
    test_normal_reply_is_not_flagged()
    test_every_steering_category_is_flagged_and_has_a_notice()
    test_categories_in_the_question_match_the_notice_table()
    test_the_question_is_the_one_that_was_measured()
    test_short_or_missing_replies_are_skipped_without_asking()
    test_long_replies_keep_start_and_end_and_stay_small()
    test_it_fails_quiet()
    test_shared_backoff_with_the_other_feature()
    test_http_client_sends_both_fields()
    test_app_wiring()
    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} check(s) FAILED:")
        for f in _FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("All checks passed.")
