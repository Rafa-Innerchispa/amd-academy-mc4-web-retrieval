# AMD AI League — Match 4: Intelligent Web Information Retrieval

**Human task ID:** `MATCH4-WEB-RETRIEVAL`  
**Active window:** October 13–27, 2026  
**Points:** 1,800  
**Current branch:** `chatgpt/mc4-core-20261019`

> Build an AI agent that can navigate websites, understand a natural-language request and accurately retrieve the specific information a user needs.

## Current state

This repository has moved beyond the original scaffold.

Implemented on the active development branch:

- bounded same-domain navigation with loop prevention
- deterministic intent parsing
- context-ranked exact-value extraction
- support for dates, versions, prices, email, phone and technical values
- HTML table extraction
- JSON-LD extraction
- exact/fuzzy evidence verification
- SHA-256 snapshot provenance
- fail-closed behavior when evidence is insufficient
- SSRF guard for localhost/private/link-local/reserved targets
- redirect target revalidation
- isolated polished demo UI under `demo/`
- additional tests for candidate ranking and URL safety

The graded adapter is intentionally **not frozen yet** because the public Match 4 page currently does not expose a usable starter-kit/grader-detail destination. The Python core has now passed **22 local tests**. The official MC3 starter kit also confirms a reusable programme-level Docker pattern, so a provisional ROCm container baseline and selfcheck have been added without pretending the Match 4 invocation schema is known.

See [docs/CHALLENGE_CONTRACT.md](docs/CHALLENGE_CONTRACT.md).

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
          └── JSON-LD
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

The design favors grounded extraction over free-form synthesis. A local AMD/ROCm model can be added as a reranker or difficult-case extractor once the official grader budget and runtime contract are known.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v tests/
```

CLI:

```bash
python3 -m src.cli \
  --query "What is the release date of ROCm 6.2?" \
  --url "https://rocm.docs.amd.com" \
  --json
```

## Demo UI

The product/demo layer is separate from the future grader image:

```bash
python -m demo.server
```

Open:

```text
http://127.0.0.1:8787
```

The UI shows:

- requested fact
- verified answer
- exact evidence source
- evidence excerpt
- snapshot SHA-256
- navigation trail
- explicit fail-closed state

This makes the capability useful and presentable without forcing presentation dependencies into the grader contract.

## Submission strategy

Priority order:

1. recover official current Match 4 grader/starter-kit contract
2. adapt the thin grader entrypoint
3. run full tests and held-out retrieval cases
4. build the exact required AMD/ROCm Docker image
5. validate on AMD hardware
6. publish image to a public registry
7. verify anonymous pull
8. re-run from the pulled public artifact
9. record immutable digest
10. submit as soon as LabLab exposes or documents the Match 4 image field

## Truth boundary

The public League page confirms the Match, dates, points and mission. It does **not**, at the time of this review, expose a usable Match 4 starter-kit/detail destination from the visible public control.

Accordingly, this repository does not present guessed Docker/grader details as official requirements.

## Project family

Canonical AMD AI League umbrella:

https://github.com/Rafa-Innerchispa/inneros-amd-ai-league-2026

Match 2 and Match 3 remain independently verified artifacts. Match 4 is an active development lane and will only be promoted in the umbrella as VERIFIED after the public container and grader evidence are complete.


## Programme-level container baseline

The user-provided official MC3 starter kit explicitly says that container rules are shared across the challenge programme and that MC2/MC3 use the same base image, size/VRAM rules and no-server/no-port shape.

This repo therefore now includes:

- `docker/Dockerfile.contract-baseline`
- `tools/selfcheck_program_rules.py`
- `docs/MC3_STARTER_KIT_LESSONS.md`
- `docs/SUBMISSION_READINESS.md`
- `docs/LABLAB_SUBMISSION.md`

These prepare the final container workflow without guessing Match 4-specific CLI or JSON fields.
