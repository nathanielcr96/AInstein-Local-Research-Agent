"""Auto-launches the two optional companion Streamlit apps (observability
dashboard, knowledge graph) as background subprocesses when the main
Chainlit app starts, so the header buttons (.chainlit/config.toml's
`header_links`) just work — no separate terminal commands to run by hand.

Idempotent by construction: checks whether the target port is already
answering before spawning anything, so this is safe to call every time
this module runs (including Chainlit's --watch dev-mode reload, which
re-executes the app module on every file save) without stacking up
duplicate processes — the same class of bug already found and fixed once
this session with background test scripts (orphaned duplicate processes
silently hammering the same resources — see README "Known limitations").

Best-effort and non-fatal: if streamlit isn't installed, or a companion
app fails to start for any reason, the main chat still works — these are
optional extras, not load-bearing for the agent itself.
"""

import logging
import socket
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent.parent.resolve()

_COMPANION_APPS = [
    {"name": "observability dashboard", "script": "observability/dashboard.py", "port": 8020},
    {"name": "knowledge graph", "script": "memory/graph_app.py", "port": 8030},
]


def _port_is_open(port: int, host: str = "127.0.0.1", timeout: float = 0.3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def launch_companion_apps() -> None:
    """Starts each companion app in the background if its port isn't
    already serving something. Uses `sys.executable` (not a hardcoded
    `streamlit` on PATH) so it runs under whichever interpreter/venv is
    already running this Chainlit process — the one with streamlit/keybert
    actually installed.
    """

    for app in _COMPANION_APPS:

        if _port_is_open(app["port"]):
            logger.info("%s already running on port %d — not starting another copy.", app["name"], app["port"])
            continue

        try:
            subprocess.Popen(
                [
                    sys.executable, "-m", "streamlit", "run", app["script"],
                    "--server.port", str(app["port"]),
                    # Streamlit listens on ALL interfaces unless told otherwise (verified:
                    # netstat showed 0.0.0.0:8020/8030, and the health endpoint answered on
                    # the machine's Wi-Fi and Hyper-V addresses). These read-only apps show
                    # research topics and usage metrics — loopback only. Also pinned in
                    # .streamlit/config.toml so the manual `streamlit run` commands in the
                    # README get it too; passing it here as well doesn't depend on the cwd.
                    "--server.address", "127.0.0.1",
                    "--server.headless", "true",
                ],
                cwd=str(PROJECT_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info("Started %s on port %d.", app["name"], app["port"])
        except Exception:
            logger.exception(
                "Could not start %s (port %d) — its header button won't work until it's run manually "
                "(`streamlit run %s --server.port %d`).",
                app["name"], app["port"], app["script"], app["port"],
            )
