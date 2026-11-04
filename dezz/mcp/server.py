#!/usr/bin/env python3
"""dezz-osint MCP server (stdio, JSON-RPC 2.0, MCP 2024-11-05).

Run:  python -m dezz.mcp.server   (or: python dezz/mcp/server.py)
Connect from any MCP client (Claude Desktop, opencode, custom):
  { "mcpServers": { "dezz-osint": { "command": "python", "args": ["-m", "dezz.mcp.server"], "cwd": "/path/to/dezz-osint" } } }

Protocol: newline-delimited JSON-RPC over stdin/stdout (also accepts
Content-Length framed messages). Methods: initialize, ping, tools/list,
tools/call, resources/list (empty), prompts/list (empty).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dezz.mcp.tools import TOOLS, execute
from dezz.config import VERSION

SERVER_INFO = {"name": "dezz-osint", "version": VERSION}
PROTOCOL = "2024-11-05"


def resp_ok(msg_id, result):
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def resp_err(msg_id, code, message):
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def handle(msg: dict):
    mid = msg.get("id")
    method = msg.get("method", "")
    params = msg.get("params", {}) or {}
    if method == "initialize":
        return resp_ok(mid, {"protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
                             "serverInfo": SERVER_INFO})
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None
    if method == "ping":
        return resp_ok(mid, {})
    if method == "tools/list":
        return resp_ok(mid, {"tools": TOOLS})
    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {}) or {}
        data = execute(name, args)
        return resp_ok(mid, {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)[:8000]}],
                                         "isError": bool(isinstance(data, dict) and data.get("error"))})
    if method in ("resources/list", "prompts/list"):
        key = "resources" if method.startswith("resources") else "prompts"
        return resp_ok(mid, {key: []})
    return resp_err(mid, -32601, f"Method not found: {method}")


def read_messages():
    """Yield parsed JSON-RPC messages from stdin (NDJSON or Content-Length framed)."""
    data = sys.stdin.buffer.read() if not sys.stdin.isatty() else sys.stdin.read()
    if isinstance(data, bytes):
        text = data.decode("utf-8", "replace")
    else:
        text = data
    if not text.strip():
        return
    # Try: whole-stream is one JSON, else NDJSON lines, else LSP-style framing
    if "Content-Length" in text:
        parts = text.split("\r\n\r\n")
        for p in parts:
            p = p.strip()
            if p.startswith("{"):
                try:
                    yield json.loads(p)
                except Exception:
                    pass
        return
    try:
        yield json.loads(text)
        return
    except Exception:
        pass
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                yield json.loads(line)
            except Exception:
                pass


def main():
    if sys.stdin.isatty():
        # interactive smoke: print tools and exit
        print(json.dumps({"server": SERVER_INFO, "protocol": PROTOCOL, "tools": [t["name"] for t in TOOLS]}, indent=2))
        return
    for msg in read_messages() or []:
        try:
            out = handle(msg)
        except Exception as e:
            out = resp_err(msg.get("id"), -32603, str(e)[:500])
        if out is not None:
            sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
