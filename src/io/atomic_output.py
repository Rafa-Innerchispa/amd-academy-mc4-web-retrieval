from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping


def write_json_atomic(path: str | Path, payload: Mapping[str, Any]) -> None:
    """Write grader output atomically.

    A temporary file is flushed and fsynced before os.replace(), so a timeout or
    process interruption is less likely to leave a partially written JSON file.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".{target.name}.{os.getpid()}.tmp")

    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
    with temp.open("w", encoding="utf-8") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temp, target)


def initialize_empty_output(path: str | Path) -> None:
    """Create a valid fail-closed placeholder before long retrieval starts."""
    write_json_atomic(
        path,
        {
            "answer": "",
            "sources": [],
            "confidence": 0.0,
        },
    )
