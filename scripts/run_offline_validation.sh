#!/usr/bin/env bash
set -euo pipefail

python3 -m compileall -q src app tools
python3 -m pytest -q
PYTHONPATH=. python3 tools/benchmark_core.py

echo
echo "LOCAL FUNCTIONAL VALIDATION COMPLETE"
echo "This does not replace AMD hardware or the official Match 4 grader."
