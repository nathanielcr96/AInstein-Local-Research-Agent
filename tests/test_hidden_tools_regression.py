"""Regression test for step 4.3 of SECURITY_IMPLEMENTATION_PLAN.md.

`graph.py`'s HIDDEN_TOOLS set is the only thing stopping the model from reaching
deepagents' filesystem tools directly — `execute` (a real shell-execution capability,
see deepagents/backends/local_shell.py) and `task` (launches subagents that do NOT
respect this same filter — see the comment above HIDDEN_TOOLS in graph.py, and
core/middleware.py's ExcludeToolsMiddleware docstring for why hiding the *name* still
matters even though this project uses FilesystemBackend, not LocalShellBackend).

This test exists so that a future edit to graph.py — someone reorganizing the tool
list, a deepagents upgrade that renames something, a merge that drops a line — fails
loudly here instead of silently reopening that surface. It is deliberately narrow: it
does not re-litigate what HIDDEN_TOOLS should contain beyond the two names this
project has already decided are load-bearing for safety.

Run with: python tests/test_hidden_tools_regression.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import graph
from core.middleware import ExcludeToolsMiddleware

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        _FAILURES.append(label)


_CRITICAL_HIDDEN_TOOLS = {"execute", "task"}


def test_execute_and_task_are_hidden():
    check(
        "'execute' is in HIDDEN_TOOLS",
        "execute" in graph.HIDDEN_TOOLS,
    )
    check(
        "'task' is in HIDDEN_TOOLS",
        "task" in graph.HIDDEN_TOOLS,
    )


def test_full_expected_set_unchanged():
    """Not just the two critical names — the whole set, so an accidental removal of
    any of the filesystem tools (ls/read_file/write_file/edit_file/glob/grep) is also
    caught, not just the two most dangerous ones."""
    expected = {"ls", "read_file", "write_file", "edit_file", "glob", "grep", "execute", "task"}
    check(
        f"HIDDEN_TOOLS == {sorted(expected)}",
        graph.HIDDEN_TOOLS == expected,
    )


def test_hidden_tools_actually_wired_into_the_middleware_stack():
    """The set existing isn't enough on its own — confirm graph.py's middleware list
    actually builds an ExcludeToolsMiddleware from HIDDEN_TOOLS (not, say, an empty
    set, or a different variable that quietly stopped being the same object)."""
    import inspect
    source = inspect.getsource(graph)
    check(
        "graph.py constructs ExcludeToolsMiddleware(excluded=HIDDEN_TOOLS)",
        "ExcludeToolsMiddleware(excluded=HIDDEN_TOOLS)" in source,
    )


def test_excluded_tool_call_is_actually_rejected():
    """End-to-end at the middleware level (no live model needed): a tool_call naming
    'execute' or 'task' must come back as an error ToolMessage, never reach a real
    handler — this is the actual enforcement mechanism, not just the config list."""
    middleware = ExcludeToolsMiddleware(excluded=graph.HIDDEN_TOOLS)

    class _FakeRequest:
        def __init__(self, name):
            self.tool_call = {"name": name, "args": {}, "id": "x"}

    def handler_that_must_not_run(request):
        raise AssertionError("handler was called for an excluded tool — HIDDEN_TOOLS did not block it")

    for name in _CRITICAL_HIDDEN_TOOLS:
        result = middleware.wrap_tool_call(_FakeRequest(name), handler_that_must_not_run)
        check(f"call to '{name}' is rejected before reaching a real handler", result.status == "error")


if __name__ == "__main__":
    test_execute_and_task_are_hidden()
    test_full_expected_set_unchanged()
    test_hidden_tools_actually_wired_into_the_middleware_stack()
    test_excluded_tool_call_is_actually_rejected()

    print()
    if _FAILURES:
        print(f"{len(_FAILURES)} check(s) FAILED:")
        for f in _FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checks passed.")
