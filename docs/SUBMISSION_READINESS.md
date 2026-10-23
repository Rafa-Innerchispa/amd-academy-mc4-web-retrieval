# Match 4 Submission Readiness

Date: 2026-10-19

## Current verdict

**NOT READY FOR FINAL LABLAB SUBMISSION YET**

The core, provisional adapter, validation harness and container baseline are implemented. The remaining blockers are the official Match 4 grader/starter-kit contract, AMD physical image validation, public artifact verification and the LabLab Match 4 submission route.

## Human task

`MATCH4-WEB-RETRIEVAL`

## Repository

`Rafa-Innerchispa/amd-academy-mc4-web-retrieval`

Development branch:

`chatgpt/mc4-core-20261019`

Draft PR:

https://github.com/Rafa-Innerchispa/amd-academy-mc4-web-retrieval/pull/2

## Implemented

- [x] bounded best-first navigation with dead-end backtracking
- [x] loop prevention
- [x] same-domain lock by default
- [x] URL + anchor-text ranking
- [x] natural-language intent parsing
- [x] exact-value candidate extraction
- [x] price/date/version/contact/hours/count/person/spec patterns
- [x] HTML table extraction
- [x] JSON-LD extraction
- [x] raw JSON/API response extraction
- [x] fail-closed verification
- [x] structured-data raw-HTML grounding
- [x] evidence URL + snapshot hash
- [x] SSRF/private-network protection by default
- [x] redirect validation before following
- [x] cross-domain redirect escape blocking
- [x] explicit internal-grader-host allowlist support
- [x] wall-clock retrieval budget
- [x] atomic output writer
- [x] path-traversal-safe grader output IDs
- [x] provisional `/app/app.py` compatibility adapter
- [x] common grader CLI aliases (`-q`, `--input-file`, `--tasks`) covered by tests
- [x] isolated demo UI
- [x] provisional programme-level Docker baseline
- [x] programme-level Docker selfcheck
- [x] one-command offline validation
- [x] MC3 starter-kit lessons captured
- [x] LabLab submission draft prepared

## Local functional validation

Executed against the current implementation:

```bash
python3 -m compileall -q src app tools
python3 -m pytest -q
PYTHONPATH=. python3 tools/benchmark_core.py
```

Results:

- **compileall: PASS**
- **74 tests passed**
- offline benchmark: **all current cases PASS**
- competitive adversarial benchmark: **30/30 PASS (synthetic, not official AMD grader)**
- lightweight container packaging smoke: **PASS** (GitHub Actions run 39342544907)
- cross-domain redirect regression: **PASS**
- structured prompt-injection regressions: **PASS**
- JSON/API extraction regressions: **PASS**
- decoy-link backtracking E2E: **PASS**

- exact-case accuracy: **1.0**
- competitive benchmark p50/p95: **3.018 / 6.429 ms**
- ambiguity gate activated: **3/30 cases (10%)**
- baseline reranker calls: **0**
- CI mocked latency p50: **2.109 ms**
- CI mocked latency p95: **3.742 ms**

Evidence:

- `evidence/ci_validation_20261019.json`
- `evidence/local_pytest_20261019.json`
- `evidence/offline_benchmark_20261019.json`

These are development-container functional results. They are not AMD GPU metrics and are not an official Match 4 grader score.

## Program-level container baseline learned from the official MC3 starter kit

The official MC3 kit states that container rules are shared across the challenge programme. It confirms the programme pattern of:

- Docker submission
- ROCm base image
- no outbound evaluation network
- no TCP service / no exposed port
- weights/dependencies shipped in-image
- hard resource/time gates
- GPU execution required

MC2 and MC3 use:

`rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`

The provisional Match 4 Dockerfile now uses that base, copies `src/` and `app/app.py`, and retains the exec-based no-port container shape.

## Critical unknowns blocking the final image

- [ ] exact Match 4 grader invocation
- [ ] exact input schema
- [ ] exact output schema
- [ ] exact network topology / target-site delivery
- [ ] exact time budgets
- [ ] exact image-size and VRAM repetition for Match 4
- [ ] exact Match 4 sample/selfcheck
- [ ] LabLab Match 4 image field or equivalent submission route

## Final-image gates

Before marking READY:

- [ ] official Match 4 contract recovered
- [x] thin provisional grader adapter implemented
- [ ] adapter narrowed to the official contract
- [ ] official sample/selfcheck green
- [x] lightweight CI container packaging smoke green
- [ ] Docker image built on AMD host
- [ ] AMD GPU use proven
- [ ] VRAM peak recorded
- [ ] startup/query/whole-run timing recorded
- [ ] image uncompressed size recorded
- [ ] runtime network behavior validated
- [ ] public registry push
- [ ] anonymous pull
- [ ] re-run from anonymously pulled artifact
- [ ] immutable digest recorded
- [ ] exact LabLab submission route confirmed

## Planned public image naming

Reserved naming only, **not yet published**:

`us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/amd-academy-mc4-web-retrieval:mc4-final`
