# LabLab Submission Draft — AMD AI League Match 4

> Draft prepared early so publication becomes a copy/paste operation once LabLab exposes the Match 4 submission field and the official grader artifact is verified.

## Project name

**InnerOS Verified Web Retrieval on AMD ROCm**

## One-line pitch

A bounded, evidence-first web retrieval agent that navigates sites, extracts the exact requested value, verifies it against source content, and fails closed when the evidence is insufficient.

## Description

InnerOS Verified Web Retrieval is our AMD AI League Match 4 implementation for Intelligent Web Information Retrieval.

The agent accepts a natural-language request and a starting web location, navigates within a bounded budget, extracts structured and unstructured candidate values, and returns only evidence-backed information.

The retrieval core is deliberately deterministic where possible:

- intent-aware exact-value extraction for prices, dates, versions, contact data and technical specifications;
- structured parsing of HTML tables and JSON-LD;
- bounded navigation with loop prevention;
- provenance for every accepted answer;
- fail-closed behavior when evidence cannot support the requested fact;
- redirect and network-target safety controls;
- configurable support for official internal grader hosts without weakening normal web defaults.

A separate demo interface makes the capability easy to use and inspect, while the graded container remains isolated and minimal.

The project is local-first and designed for AMD ROCm. The final Match 4 Docker artifact will use the official challenge runtime and will be published only after the official Match 4 starter kit/contract is recovered and the image passes AMD hardware, resource, timing and anonymous-pull validation.

## Why AMD

The challenge artifact is designed around the AMD AI League container model: AMD ROCm runtime, GPU execution, reproducible local inference/extraction, no paid external inference dependency, and strict evidence-driven behavior.

The broader InnerOS architecture uses AMD hardware as a local execution layer for governed agent workflows. Match 4 validates web retrieval as another independently testable capability before promotion into the wider platform.

## Key technologies

- AMD ROCm
- AMD Radeon AI PRO R9700
- Python
- Docker
- BeautifulSoup
- Requests
- structured web extraction
- JSON-LD
- evidence provenance
- bounded agent navigation
- InnerOS

## GitHub

Repository:

https://github.com/Rafa-Innerchispa/amd-academy-mc4-web-retrieval

Development branch:

`chatgpt/mc4-core-20261019`

## Docker image

**PLANNED FINAL URI — NOT YET PUBLISHED**

`us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/amd-academy-mc4-web-retrieval:mc4-final`

Digest:

`PENDING_OFFICIAL_MC4_CONTRACT_AND_FINAL_BUILD`

## Verification

Current Python core:

- **22 local tests passed**
- bounded navigation: PASS
- fail-closed grounding: PASS
- JSON-LD extraction: PASS
- HTML table extraction: PASS
- private-network blocking by default: PASS
- redirect-to-private-target blocking: PASS
- explicit internal grader-host allowlisting: PASS

Final AMD Docker metrics remain pending until the official Match 4 contract is available.

## Submission truth boundary

This draft does not claim the Docker image is final or publicly available yet. Match 4-specific grader invocation/output requirements remain intentionally unfrozen until AMD/LabLab publishes the official contract.
