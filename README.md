# AMD AI League — Match 4: Intelligent Web Information Retrieval

**Human task ID:** `MATCH4-WEB-RETRIEVAL`  
**Active window:** October 13–27, 2026  
**Points:** 1,800  
**Current branch:** `chatgpt/mc4-core-20261019`

> Build an AI agent that can navigate websites, understand a natural-language request and accurately retrieve the specific information a user needs.

## Current state

This repository is now an active Match 4 implementation rather than a scaffold.

Implemented on the development branch:

- bounded best-first same-domain navigation with loop prevention and dead-end backtracking
- URL + visible-anchor ranking for opaque links
- deterministic intent parsing
- context-ranked exact-value extraction
- prices, dates, versions, email, phone, opening hours, counts, people and technical values
- HTML table extraction
- JSON-LD and raw JSON/API response extraction
- mailto/tel extraction
- exact/fuzzy evidence verification
- raw-HTML grounding for structured data
- SHA-256 provenance with coordinate-space tracking
- fail-closed behavior when evidence is insufficient
- SSRF/private/link-local/loopback blocking by default
- redirect validation before following, including cross-domain redirect escape blocking
- explicit allowlist for grader-provided internal hosts
- bounded wall-clock retrieval budget
- atomic JSON output helpers
- path-traversal-safe, bounded grader output IDs
- provisional `/app/app.py` grader adapter
- common grader CLI aliases (`-q`, `--input-file`, `--tasks`) for compatibility without changing fail-closed semantics
- isolated product/demo UI under `demo/`
- provisional ROCm programme-level Docker baseline
- repeatable offline validation and image-release runbooks

## Current local evidence

Development validation on the current implementation:

- **65 tests passed**
- `python3 -m compileall -q src app tools`: **PASS**
- offline retrieval benchmark: **all current cases PASS**
- lightweight container packaging smoke: **PASS** (GitHub Actions run 39342544907)

- exact-case accuracy: **1.0**
- CI mocked benchmark p50: **2.109 ms**
- CI mocked benchmark p95: **3.742 ms**
- adversarial coverage: JSON/API responses, structured prompt injection, cross-domain redirects, absolute deadline enforcement, fragment deduplication, decoy-link backtracking, and current-vs-stale conflicting values

Evidence:

- `evidence/ci_validation_20261019.json`
- `evidence/local_pytest_20261019.json`
- `evidence/offline_benchmark_20261019.json`

These are local functional results, **not AMD hardware performance and not an official LabLab score**.

## Architecture

```text
Natural-language request
          │
          ▼
    Intent parser
          │
          ▼
 Bounded navigator ─── URL safety policy
          │
          ▼
  HTML / structured data
          │
          ├── clean text
          ├── tables
          ├── JSON-LD
          ├── raw JSON / APIs
          └── mailto / tel
          │
          ▼
 Context-ranked candidates
          │
          ▼
 Fail-closed verifier
          │
          ├── unsupported → refusal
          └── verified → exact answer + source + snapshot hash
```

The design favors grounded extraction over free-form synthesis. A local AMD/ROCm model can still be added as a difficult-case reranker once the official grader budget and runtime contract are known.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/run_offline_validation.sh
```

CLI:

```bash
python3 -m src.cli \
  --query "What is the release date of ROCm 6.2?" \
  --url "https://rocm.docs.amd.com" \
  --json
```

## Provisional grader adapter

The branch includes `app/app.py` as a tolerant compatibility layer while the official Match 4 contract remains unavailable publicly.

It supports common query/ID/start-URL aliases, batch JSON input, atomic output, and fail-closed empty results. This adapter is intentionally replaceable and will be narrowed to the exact official schema once AMD/LabLab publishes the Match 4 starter kit.

## Demo UI

The product/demo layer is separate from the graded image:

```bash
python -m demo.server
```

Open:

```text
http://127.0.0.1:8787
```

It shows the requested fact, verified answer, evidence source, evidence excerpt, snapshot SHA-256, navigation trail and explicit fail-closed state.

## Programme-level container baseline

The user-provided official MC3 starter kit says container rules are shared across the challenge programme and that MC2/MC3 use the same base image, size/VRAM rules and no-server/no-port shape.

This repo therefore includes:

- `docker/Dockerfile.contract-baseline`
- `.dockerignore`
- `tools/selfcheck_program_rules.py`
- `scripts/build_contract_baseline.sh`
- `scripts/validate_contract_baseline.sh`
- `docs/MC3_STARTER_KIT_LESSONS.md`
- `docs/IMAGE_RELEASE_RUNBOOK.md`
- `docs/SUBMISSION_READINESS.md`
- `docs/LABLAB_SUBMISSION.md`

The provisional Dockerfile already copies the retrieval core and `/app/app.py` into the ROCm 10 baseline while keeping the no-port execution model.

## Submission strategy

1. recover the official Match 4 starter kit / grader contract
2. reduce the compatibility adapter to the exact required schema
3. run official sample/selfcheck
4. build on AMD hardware
5. prove GPU use, timing, VRAM and uncompressed image size
6. publish the public image
7. verify anonymous pull
8. re-run the pulled image on AMD
9. record immutable digest
10. submit when LabLab exposes or documents the Match 4 submission route

## Truth boundary

The public League page confirms Match 4, dates, points and mission. It does not currently expose a usable Match 4 starter-kit/detail destination from the visible public control.

Accordingly, this repository does not present guessed Match 4 grader details as official requirements.

## Project family

Canonical AMD AI League umbrella:

https://github.com/Rafa-Innerchispa/inneros-amd-ai-league-2026

Match 2 and Match 3 remain independently verified artifacts. Match 4 remains **ACTIVE DEVELOPMENT** until the final public container and official grader evidence are complete.
