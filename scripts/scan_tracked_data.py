"""Read-only scan of everything git tracks for things that shouldn't be published: API keys,
tokens, private keys, the values in your local `.env`, e-mail addresses, and your local user
name / absolute paths. It never modifies or deletes anything and never prints a secret in full
(samples are masked).

Why this exists (SECURITY_REVIEW.md): several data files are tracked on purpose, as real example
data for people who clone the repo — long_term.md, graph.sqlite, embeddings.sqlite,
chainlit_data.sqlite (the conversation history the sidebar shows), checkpoints.sqlite (the full
agent state of every conversation, tool results included), observability/metrics.sqlite and
conversation_history/. Keeping them is a legitimate choice; this shows what is inside them, so
the choice is made knowing it, and can be re-checked before every push:

    python scripts/scan_tracked_data.py            # summary
    python scripts/scan_tracked_data.py --samples 5

Exit code 1 if anything HIGH was found (a secret-looking value), 0 otherwise — usable as a
pre-push check. Local paths, e-mail addresses and the user name are reported as INFO/MEDIUM and
don't fail the run: they are privacy details to decide on, not credentials.
"""
import argparse
import getpass
import re
import sqlite3
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MAX_TEXT_BYTES = 40 * 1024 * 1024

# arXiv paper text (raw/child/parent chunks): third-party, public by nature, and full of author
# e-mails and example paths that would drown out what is actually yours. Skipped unless asked.
PAPER_DIRS = ("papers/raw/", "papers/child/", "papers/parent/")

# (name, severity, regex)
PATTERNS = [
    ("OpenAI-style key", "HIGH", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("HuggingFace token", "HIGH", re.compile(r"\bhf_[A-Za-z0-9]{30,}")),
    ("GitHub token", "HIGH", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("AWS access key id", "HIGH", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Slack token", "HIGH", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("JWT", "HIGH", re.compile(r"\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}")),
    ("private key block", "HIGH", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("key/secret/password assignment", "HIGH",
     re.compile(r"(?i)\b(api[_-]?key|secret|passwd|password|auth[_-]?token)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-/+]{16,}")),
    ("e-mail address", "MEDIUM", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+\b")),
    ("absolute Windows user path", "MEDIUM", re.compile(r"[A-Za-z]:\\{1,2}Users\\{1,2}[^\\/\s\"'<>|]+")),
    ("absolute Unix home path", "MEDIUM", re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+")),
    ("private-network IP (LAN)", "INFO", re.compile(r"\b(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b")),
]

# Text that legitimately looks like an e-mail / path inside a tracked file and isn't yours.
BENIGN_EMAILS = re.compile(r"@(?:example\.(?:com|org)|users\.noreply\.github\.com)$|^noreply@|^git@github\.com$")
# JS/Python package "e-mails" such as name@1.2.3 are not matched by the regex (needs a dotted TLD),
# but scoped npm packages and decorators can be; these are not addresses.
BENIGN_EMAIL_LOCALPARTS = ("@babel", "@types", "@radix", "@vitejs")


def mask(value: str) -> str:
    value = value.strip()
    return value if len(value) <= 8 else f"{value[:4]}…{value[-2:]} ({len(value)} chars)"


def tracked_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True).stdout
    return [REPO / p for p in out.decode("utf-8").split("\0") if p]


def env_secret_values() -> dict[str, str]:
    """Values from the local .env (which is gitignored) — looking for THEM inside tracked files
    is the most direct leak test there is. Only the key name is ever printed."""
    env = REPO / ".env"
    values = {}
    if env.exists():
        for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, _, val = line.partition("=")
                val = val.strip().strip("'\"")
                if len(val) >= 8:
                    values[key.strip()] = val
    return values


def iter_sqlite_text(path: Path):
    """Yield (location, text) for every text/blob cell, skipping the float-vector blobs of the
    embedding cache (binary noise, nothing human-written)."""
    conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        for (table,) in conn.execute("select name from sqlite_master where type='table'").fetchall():
            cols = [r[1] for r in conn.execute(f'pragma table_info("{table}")')]
            for row in conn.execute(f'select * from "{table}"'):
                for col, cell in zip(cols, row):
                    if isinstance(cell, bytes):
                        if path.name == "embeddings.sqlite":
                            continue
                        cell = cell.decode("utf-8", errors="ignore")
                    if isinstance(cell, str) and cell:
                        yield f"{table}.{col}", cell
    finally:
        conn.close()


def iter_file_text(path: Path):
    if path.suffix == ".sqlite":
        yield from iter_sqlite_text(path)
        return
    if path.stat().st_size > MAX_TEXT_BYTES:
        return
    data = path.read_bytes()
    if b"\0" in data[:4096]:  # binary
        return
    yield "text", data.decode("utf-8", errors="ignore")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--samples", type=int, default=3, help="masked samples to show per finding (default 3)")
    ap.add_argument("--include-papers", action="store_true", help="also scan the arXiv paper text under papers/")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    secrets = env_secret_values()
    username = getpass.getuser()
    extra = [("value from your local .env", "HIGH", None), (f"local user name '{username}'", "MEDIUM", None)]

    hits: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    severities = {name: sev for name, sev, _ in PATTERNS} | {n: s for n, s, _ in extra}
    scanned = 0

    for path in tracked_files():
        if not path.is_file():
            continue
        rel = path.relative_to(REPO).as_posix()
        if not args.include_papers and rel.startswith(PAPER_DIRS):
            continue
        try:
            cells = list(iter_file_text(path))
        except sqlite3.DatabaseError:
            continue
        scanned += 1
        for where, text in cells:
            for name, _sev, rx in PATTERNS:
                for m in rx.finditer(text):
                    found = m.group(0)
                    if name == "e-mail address" and (
                        BENIGN_EMAILS.search(found)
                        or found.startswith(BENIGN_EMAIL_LOCALPARTS)
                        or re.fullmatch(r"[\d.]+", found.split("@", 1)[1])  # package@1.2.3, not a mailbox
                    ):
                        continue
                    hits[name][f"{rel} [{where}]"].append(mask(found))
            for key, val in secrets.items():
                if val in text:
                    hits["value from your local .env"][f"{rel} [{where}]"].append(f"the value of {key}")
            if username and re.search(rf"(?<![A-Za-z0-9]){re.escape(username)}(?![A-Za-z0-9])", text):
                hits[f"local user name '{username}'"][f"{rel} [{where}]"].append(username)

    print(f"scanned {scanned} tracked files (read-only)\n")
    order = {"HIGH": 0, "MEDIUM": 1, "INFO": 2}
    high = 0
    for name in sorted(hits, key=lambda n: (order[severities[n]], n)):
        sev = severities[name]
        total = sum(len(v) for v in hits[name].values())
        files = len({loc.split(" [")[0] for loc in hits[name]})
        print(f"[{sev}] {name}: {total} occurrence(s) in {files} file(s)")
        if sev == "HIGH":
            high += total
        for loc, samples in sorted(hits[name].items(), key=lambda kv: -len(kv[1]))[:6]:
            shown = ", ".join(sorted(set(samples))[: args.samples])
            print(f"    {loc}: {len(samples)}x  e.g. {shown}")
        print()

    if not hits:
        print("nothing found.")
    print("HIGH findings:", high)
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
