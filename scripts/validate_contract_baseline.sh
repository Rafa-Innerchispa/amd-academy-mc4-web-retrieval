#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${1:-amd-academy-mc4-web-retrieval:contract-baseline}"

python3 tools/selfcheck_program_rules.py "${IMAGE_TAG}"

echo
echo "Manual AMD checks still required before any final submission claim:"
echo "  - prove AMD GPU use"
echo "  - record peak VRAM"
echo "  - record uncompressed image size"
echo "  - run the official Match 4 selfcheck/sample when released"
