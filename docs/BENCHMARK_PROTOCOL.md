# Offline Retrieval Benchmark

The official Match 4 starter kit is not yet publicly recoverable, so this repository carries a deterministic local benchmark that exercises the retrieval core without pretending to be the official grader.

Run:

```bash
PYTHONPATH=. python3 tools/benchmark_core.py
```

Current case families:

- direct price
- release date
- version
- technical specification from a table
- JSON-LD price
- opaque multi-hop navigation with a misleading decoy value
- opening hours
- contact email
- fail-closed missing answer

The harness records exact case accuracy, source/provenance correctness, navigation steps, per-case latency, p50/p95 latency and refusal correctness.

## Why this exists

Public Match 4 submissions suggest exact-value retrieval, evidence URLs, bounded navigation and low latency are useful design targets, but public submissions are **not** the official contract.

This benchmark therefore targets robust general behavior while remaining replaceable by the official sample/selfcheck when AMD/LabLab releases it.

## Benchmark policy

A case passes only when all applicable conditions match:

1. success/refusal state
2. exact expected answer
3. exact expected source URL

No partial credit is assigned by this harness.

## Current evidence

The benchmark has now been executed on the current development implementation and retained at:

`evidence/offline_benchmark_20261019.json`

Result:

- **9/9 cases PASS**
- exact-case accuracy: **1.0**
- CI mocked p50: **1.364 ms**
- CI mocked p95: **36.989 ms**

These timings come from mocked local pages in a development container. They are useful regression evidence, not AMD hardware performance and not an official competition score.
