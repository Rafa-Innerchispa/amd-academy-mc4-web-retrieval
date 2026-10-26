# Program-level container rules learned from the official MC3 starter kit

Source reviewed: user-provided official mc3-starter-kit.zip.

This document records program-level submission mechanics that the MC3 contract explicitly says are shared across the challenge programme, while keeping Match 4-specific grader details separate until the Match 4 kit is published.

## What MC3 explicitly establishes

The MC3 contract states that the container rules are the same for every challenge in the programme. It also states that MC2 used the same base image, size/VRAM limits, and the same no-server/no-port container shape.

Program-level baseline:

- submission artifact: Docker image
- AMD ROCm base image family
- MC2 and MC3 exact base: rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0
- image size ceiling: 60 GiB uncompressed
- VRAM band: 1-48 GiB, with 1% tolerance on the upper limit in MC3
- evaluation has no outbound network
- model weights and dependencies needed at runtime must ship inside the image
- container should not expose or require a TCP service or port
- the harness starts the container, then executes commands inside it
- GPU use is mandatory; CPU-only execution is rejected
- timeouts are hard gates, not soft scoring factors

## What remains Match-specific

Do not copy these MC3-specific details into Match 4 unless the MC4 contract says so:

- --index /app/corpus
- --query-id
- /app/output/<query-id>_output.json
- exactly ten questions
- answer/citations/confidence schema
- MC3 corpus types and citation rules
- MC3-specific timing values
- MC3 resident-model recommendation behind a Unix socket

## Engineering consequence for Match 4

We can prepare a container baseline now:

1. use the same ROCm 10 base as a provisional programme baseline;
2. make the container stay alive without opening a port;
3. bake all Python dependencies into the image;
4. keep the retrieval engine under /app/src;
5. keep the future MC4 grader adapter thin and replaceable;
6. avoid runtime downloads;
7. build a self-check for programme-level rules.

We should not freeze the final Match 4 entrypoint or output schema until the official MC4 starter kit or contract is available.

## Why this matters

The MC3 kit makes clear that catastrophic failures happen at the contract boundary rather than in model quality: wrong base layer, oversized image, no GPU use, runtime downloads, wrong output location, timeouts, or malformed output.

For Match 4, retrieval quality matters only after the container survives those hard gates.
