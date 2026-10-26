# LabLab Submission — AMD AI League Match 4

Updated: 2026-10-26

## Publication state

**General LabLab project publication: READY**

**Official Mini-Challenge 4 evaluator/image submission: NOT PUBLICLY AVAILABLE YET**

The public AMD AI League dashboard still exposes official evaluator results for MC2 and MC3 only. This document is ready for the general project page now and must not be presented as an official MC4 grading receipt.

## Project name

**InnerOS Verified Web Retrieval on AMD ROCm**

## One-line pitch

A bounded, evidence-first web retrieval agent that navigates sites, extracts the exact requested value, verifies it against source content, and fails closed when the evidence is insufficient.

## Short description

InnerOS Verified Web Retrieval converts natural-language requests into exact, source-backed answers. It combines deterministic intent parsing, bounded web navigation, structured extraction and strict verification, returning an answer only when the cited page proves it.

## Full description

InnerOS Verified Web Retrieval is our AMD AI League Match 4 implementation for Intelligent Web Information Retrieval.

The agent accepts a natural-language request and a starting web location, navigates within a bounded budget, extracts candidate values from structured and unstructured content, and emits only evidence-backed information.

Core capabilities:

- exact-value extraction for prices, dates, versions, contacts, opening hours, counts, people and technical specifications;
- HTML table, JSON-LD and raw JSON/API extraction;
- bounded best-first navigation with loop prevention and dead-end backtracking;
- anchor-aware link ranking and pagination;
- exact source URL plus SHA-256 provenance;
- fail-closed behavior when the evidence cannot support the requested answer;
- prompt-injection rejection for untrusted page content;
- SSRF, private-address and redirect-escape protections;
- atomic, path-safe grader output;
- an optional ambiguity gate for a local grounded reranker without allowing the model to invent new values.

The implementation is local-first and has no paid external inference dependency. The production AMD host now runs ROCm 10.1 on a Radeon AI PRO R9700, while the challenge-container adapter remains isolated so it can be narrowed to the exact official grader contract when AMD/LabLab publishes it.

## Why AMD

The project uses AMD as a real local execution platform, not merely a logo in a slide deck:

- AMD Radeon AI PRO R9700 (`gfx1201`);
- ROCm 10.1 production runtime;
- PyTorch 2.13.0+rocm10.1.0;
- vLLM 0.29.1 development runtime;
- Qwen3-Coder 30B AWQ available locally for selective semantic reasoning;
- deterministic retrieval remains the fast baseline, avoiding unnecessary GPU use for facts already present in tables or JSON.

This design combines exact extraction speed with optional AMD-accelerated reasoning only for genuinely ambiguous cases.

## Current verification

Physical AMD-host validation on 2026-10-26:

- pytest: **74/74 PASS**
- core benchmark: **16/16 PASS**
- core exact-case accuracy: **1.0**
- core p50 / p95: **1.707 / 4.754 ms**
- competitive adversarial benchmark: **30/30 PASS**
- competitive exact-case accuracy: **1.0**
- competitive p50 / p95: **1.186 / 2.763 ms**
- live ROCm 10.1 runtime probe: **ROCM101_OK**

Evidence:

`docs/evidence/amd_rocm101_host_validation_20261026.json`

These are deterministic engineering benchmarks. They are not an official AMD grader score and are not directly comparable with competitors using different private datasets.

## Key technologies

- AMD ROCm
- AMD Radeon AI PRO R9700
- Python
- Docker
- Qwen3-Coder
- BeautifulSoup
- Requests
- JSON-LD
- bounded agent navigation
- evidence provenance
- InnerOS

## Repository

https://github.com/Rafa-Innerchispa/amd-academy-mc4-web-retrieval

Active development branch:

`chatgpt/mc4-core-20261019`

Draft PR:

https://github.com/Rafa-Innerchispa/amd-academy-mc4-web-retrieval/pull/2

## Docker image

Reserved final URI, not yet published:

`us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/amd-academy-mc4-web-retrieval:mc4-final`

Digest:

`PENDING_OFFICIAL_MC4_CONTRACT_AND_FINAL_BUILD`

## Submission truth boundary

The project page can be published now. Do not claim that the Docker image has been submitted to an official MC4 evaluator until LabLab exposes the route and the final image passes the official contract, anonymous pull and AMD re-run gates.
