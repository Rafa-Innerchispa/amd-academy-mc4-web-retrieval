#!/usr/bin/env python3
"""Programme-level preflight for AMD AI League container images.

This checks only cross-challenge rules evidenced by the official MC3 starter kit.
It deliberately avoids assuming the still-unpublished Match 4 grader interface.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import time
import uuid

MAX_IMAGE_GIB = 60.0


def run(args, timeout=120):
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def parse_size(value: str) -> int:
    value = value.strip()
    match = re.fullmatch(r"([0-9.]+)\s*([kKmMgGtT]?[iI]?[bB])?", value)
    if not match:
        raise ValueError(value)
    number = float(match.group(1))
    unit = (match.group(2) or "B").lower()
    factors = {
        "b": 1,
        "kb": 1000,
        "kib": 1024,
        "mb": 1000**2,
        "mib": 1024**2,
        "gb": 1000**3,
        "gib": 1024**3,
        "tb": 1000**4,
        "tib": 1024**4,
    }
    return int(number * factors[unit])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    args = parser.parse_args()
    passed = True

    print("1. Inspect uncompressed layer sum")
    hist = run(["docker", "history", "--no-trunc", "--format", "{{.Size}}", args.image])
    if hist.returncode != 0:
        print("  FAIL:", hist.stderr.strip())
        return 1

    total = 0
    for line in hist.stdout.splitlines():
        try:
            total += parse_size(line)
        except Exception:
            print("  WARN: could not parse", line)

    total_gib = total / (1024**3)
    if total_gib >= MAX_IMAGE_GIB:
        print(f"  FAIL: {total_gib:.2f} GiB >= {MAX_IMAGE_GIB:.0f} GiB")
        passed = False
    else:
        print(f"  PASS: {total_gib:.2f} GiB < {MAX_IMAGE_GIB:.0f} GiB")

    print("2. Start with outbound network disabled")
    name = f"mc4-preflight-{uuid.uuid4().hex[:8]}"
    started = time.monotonic()
    up = run(["docker", "run", "-d", "--network", "none", "--name", name, args.image])
    if up.returncode != 0:
        print("  FAIL:", up.stderr.strip())
        return 1

    try:
        print(f"  PASS: container started in {time.monotonic() - started:.2f}s")

        print("3. Import retrieval core inside container")
        check = run([
            "docker", "exec", name, "python3", "-c",
            "from src.agent import WebRetrievalAgent; print('core-import-ok')",
        ])
        if check.returncode != 0:
            print("  FAIL:", (check.stderr or check.stdout).strip())
            passed = False
        else:
            print("  PASS: core-import-ok")
    finally:
        run(["docker", "rm", "-f", name])

    print("4. Final AMD host checks still required")
    print("  Verify GPU use, peak VRAM, final image size, and the Match 4-specific grader adapter.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
