"""The context the app asks Ollama for is capped (graph.MAX_NUM_CTX), not the model's own maximum.

Measured with scratch/ctx_probe.py on the reference laptop (6 GB GPU, 15 GB RAM, qwen3.5:4b, prompt of ~16,400 tokens):
32,768 -> 4.8 GB in memory, 79% on the GPU, 13 tokens/s; 65,536 -> 6.1 GB, 62%, 4.7 tokens/s; 131,072 -> 8.6 GB, 44%, 3.6 tokens/s.
The cap has to stay above the recommended minimum (the prompt alone is ~19,100 tokens) and app.py has to apply it.

Run with: python tests/test_context_cap.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import graph

_FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {label}")
    if not condition:
        _FAILURES.append(label)


check("the cap is 32,768 tokens", graph.MAX_NUM_CTX == 32_768)
check("the cap is above the recommended minimum and the measured prompt",
      graph.MAX_NUM_CTX > graph.MIN_RECOMMENDED_NUM_CTX > graph.MEASURED_PROMPT_TOKENS)
src = (Path(__file__).resolve().parent.parent / "app.py").read_text(encoding="utf-8").replace("\r\n", "\n")
check("app.py asks for the smaller of the model's own limit and the cap",
      'num_ctx = min(models_info[settings["model"]]["context_length"], MAX_NUM_CTX)' in src)
check("the 'context window too small' warning still looks at the model's capped value, so a small model still warns",
      src.index("num_ctx = min(") < src.index("if num_ctx < MIN_RECOMMENDED_NUM_CTX"))
check("the agent and the metrics both use that same value",
      src.count("num_ctx = num_ctx,") == 2)

print()
if _FAILURES:
    print(f"{len(_FAILURES)} FAILED")
    sys.exit(1)
print("ALL PASSED")
