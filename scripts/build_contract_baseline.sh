#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${1:-amd-academy-mc4-web-retrieval:contract-baseline}"

docker build \
  -f docker/Dockerfile.contract-baseline \
  -t "${IMAGE_TAG}" \
  .

echo "Built ${IMAGE_TAG}"
echo "Next: python3 tools/selfcheck_program_rules.py ${IMAGE_TAG}"
