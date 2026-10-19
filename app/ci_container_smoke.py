#!/usr/bin/env python3
from __future__ import annotations

import json
import socket
import tempfile
from pathlib import Path

from app import main as app_main


def run_smoke() -> int:
    assert app_main(["--warmup"]) == 0

    with tempfile.TemporaryDirectory() as tmp:
        assert app_main([
            "--query-id", "q1",
            "--query", "What is the price of Widget Pro?",
            "--output-dir", tmp,
        ]) == 0
        payload = json.loads((Path(tmp) / "q1_output.json").read_text())
        assert payload["answer"] == ""
        assert payload["sources"] == []
        assert payload["confidence"] == 0.0

    sock = socket.socket()
    try:
        assert sock.connect_ex(("127.0.0.1", 8787)) != 0
    finally:
        sock.close()

    print("container-smoke-pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_smoke())
