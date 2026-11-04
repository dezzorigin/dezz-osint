"""TorBot adapter — HONEST, Tor-gated.

TorBot (DedSecInside/TorBot) crawls .onion sites and REQUIRES a running Tor
service. This environment has no `tor` binary, so scans cannot run here.
Nothing is faked: status() reports availability, scan() refuses loudly
without Tor instead of returning dummy data.
"""
from __future__ import annotations
import shutil
from dezz.config import WORKSPACE

TORBOT_DIR = WORKSPACE / "dedsecinside-torbot"


def status() -> dict:
    tor = shutil.which("tor")
    try:
        import stem  # noqa
        has_stem = True
    except ImportError:
        has_stem = False
    return {"checkout": str(TORBOT_DIR),
            "present": (TORBOT_DIR / "main.py").exists(),
            "tor_binary": bool(tor), "stem_lib": has_stem,
            "runnable": bool(tor) and (TORBOT_DIR / "main.py").exists(),
            "enable_hint": None if tor else "apt install tor && sudo systemctl start tor, then: cd dedsecinside-torbot && python main.py -u <onion-url>"}


def scan(onion_url: str) -> dict:
    """Run a real TorBot scan — only if Tor is available, else honest error."""
    st = status()
    if not st["runnable"]:
        raise RuntimeError(f"TorBot cannot run here: tor_binary={st['tor_binary']}. {st['enable_hint']}")
    raise NotImplementedError("Tor is present but live .onion scan passthrough not yet wired — refusing to fake it.")
