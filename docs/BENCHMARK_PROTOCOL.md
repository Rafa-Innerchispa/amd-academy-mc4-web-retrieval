# Offline Retrieval Benchmark

The official Match 4 starter kit is not yet publicly recoverable, so this repository carries a deterministic local benchmark that exercises the retrieval core without pretending to be the official grader.

Run:

```bash
python3 tools/benchmark_core.py
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

The harness records:

- exact case accuracy
- source/provenance correctness
- navigation steps
- per-case latency
- p50 latency
- p95 latency
- refusal correctness

## Why this exists

Public Match 4 submissions already suggest that the evaluation rewards exact-value retrieval, evidence URLs, bounded navigation and low latency, but those public submissions are **not** the official contract.

This benchmark therefore targets robust general behavior while remaining replaceable by the official sample/selfcheck when AMD/LabLab releases it.

## Benchmark policy

A case passes only when all applicable conditions match:

1. success/refusal state
2. exact expected answer
3. exact expected source URL

No partial credit is assigned by this harness.

## Evidence status

Do not publish benchmark scores in LabLab or the umbrella repository until the harness has been executed on the current branch and its JSON output has been retained under `evidence/`.
