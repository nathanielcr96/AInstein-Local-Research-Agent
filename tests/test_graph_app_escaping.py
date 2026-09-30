"""Regression test for the stored XSS found in memory/graph_app.py (SECURITY_REVIEW.md, finding #10).

Node labels are paper titles / author names / keywords — text a third party controls — and the
graph app pastes them as JSON inside an inline <script> block. `json.dumps` doesn't escape "<",
so a title containing `</script><script>...` ended the block early and ran as code on page load
(verified live, no click needed). The fix escapes <, >, & and the JS line terminators.

graph_app.py is a Streamlit script (it renders at import time), so this test extracts just
`_json_for_script_tag` from its source with `ast` and runs that function in isolation.
The rest of the fix — esc() around the two places node names are injected as HTML (the
nodeLabel tooltip and the click info box) — lives in the page's own JavaScript and was
verified live in a browser, not here; the last check below only guards that those calls stay.

No Ollama, no browser. Run with: python tests/test_graph_app_escaping.py
"""
import ast
import json
import sys
from pathlib import Path

GRAPH_APP = Path(__file__).resolve().parent.parent / "memory" / "graph_app.py"

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        _FAILURES.append(label)


def load_function():
    source = GRAPH_APP.read_text(encoding="utf-8")
    tree = ast.parse(source)
    fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_json_for_script_tag"), None)
    if fn is None:
        return None, source
    namespace = {"json": json}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(GRAPH_APP), "exec"), namespace)
    return namespace["_json_for_script_tag"], source


PAYLOADS = [
    "x</script><script>new Image().src='http://evil.example/x'</script>",
    "</SCRIPT><script>alert(1)</script>",
    "<!-- <script>",
    "<img src=x onerror=alert(1)>",
    "a & b < c > d",
    "línea separada fin",
    'comillas " y \' y \\ barra',
]


def main():
    fn, source = load_function()
    check("_json_for_script_tag exists in memory/graph_app.py", fn is not None)
    if fn is None:
        return

    for payload in PAYLOADS:
        data = {"nodes": [{"id": "n1", "name": payload, "type": "paper"}], "links": []}
        out = fn(data)
        check(f"no raw '<' / '>' / '&' in the embedded JSON: {payload[:40]!r}", not any(c in out for c in "<>&"))
        check(f"no raw U+2028/2029: {payload[:40]!r}", " " not in out and " " not in out)
        check(f"'</script' can't appear even case-insensitively: {payload[:40]!r}", "</script" not in out.lower())
        check(f"round-trips to the original data: {payload[:40]!r}", json.loads(out) == data)

    check(
        "the info box and the tooltip still go through esc()",
        "esc(node.name)" in source and "esc(n.name)" in source,
    )
    check("graph_json is built by the escaping function", "graph_json = _json_for_script_tag(" in source)


if __name__ == "__main__":
    main()
    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} check(s) FAILED:")
        for f in _FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    print("All checks passed.")
