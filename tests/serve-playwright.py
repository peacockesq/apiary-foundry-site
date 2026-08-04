#!/usr/bin/env python3
"""Serve the static site and exit when the owning Playwright runner dies."""

from __future__ import annotations

import argparse
import os
import signal
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def _owner_fingerprint(pid: int) -> str | None:
    """Return a Linux process start-time fingerprint, when available."""
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
    except (FileNotFoundError, PermissionError, OSError):
        return None
    return fields[21] if len(fields) > 21 else None


def _owner_alive(pid: int, fingerprint: str | None) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass

    current_fingerprint = _owner_fingerprint(pid)
    return fingerprint is None or current_fingerprint == fingerprint


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--owner-pid", type=int, required=True)
    parser.add_argument("--directory", default="..")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if not 1 <= args.port <= 65535:
        raise SystemExit("--port must be between 1 and 65535")
    if args.owner_pid <= 0:
        raise SystemExit("--owner-pid must be positive")

    owner_fingerprint = _owner_fingerprint(args.owner_pid)
    if not _owner_alive(args.owner_pid, owner_fingerprint):
        raise SystemExit("Playwright runner exited before the static server started")

    handler = partial(SimpleHTTPRequestHandler, directory=args.directory)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    server.daemon_threads = True

    def stop_when_owner_exits() -> None:
        while _owner_alive(args.owner_pid, owner_fingerprint):
            time.sleep(0.1)
        server.shutdown()

    watcher = threading.Thread(target=stop_when_owner_exits, daemon=True)
    watcher.start()

    def stop_server(_signum: int, _frame: object) -> None:
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop_server)
    signal.signal(signal.SIGINT, stop_server)

    try:
        server.serve_forever(poll_interval=0.1)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
