# Match 4 Submission Readiness

Date: 2026-10-19

## Current verdict

**NOT READY FOR FINAL LABLAB SUBMISSION YET**

The core is actively developed and locally validated, but the official Match 4 grader/starter-kit contract and the LabLab Match 4 image field are not yet exposed in the public flow we can verify.

## Human task

`MATCH4-WEB-RETRIEVAL`

## Repository

`Rafa-Innerchispa/amd-academy-mc4-web-retrieval`

Development branch:

`chatgpt/mc4-core-20261019`

Draft PR:

https://github.com/Rafa-Innerchispa/amd-academy-mc4-web-retrieval/pull/2

## Implemented

- [x] bounded navigation
- [x] loop prevention
- [x] same-domain lock by default
- [x] natural-language intent parsing
- [x] exact-value candidate extraction
- [x] price/date/version/contact/spec patterns
- [x] HTML table extraction
- [x] JSON-LD extraction
- [x] fail-closed verification
- [x] evidence URL + snapshot hash
- [x] SSRF/private-network protection by default
- [x] redirect validation before following
- [x] explicit internal-grader-host allowlist support
- [x] isolated demo UI
- [x] provisional programme-level Docker baseline
- [x] programme-level Docker selfcheck
- [x] MC3 starter-kit lessons captured

## Local validation

A local mirror of the current branch source/tests was executed with:

`python -m pytest -q`

Result:

**22 last verified; 3 new navigation/entity tests pending rerun**

This validates the Python retrieval core and safety tests. It is **not** a substitute for final AMD Docker validation.

## Program-level container baseline learned from the official MC3 starter kit

The official MC3 kit states that container rules are shared across the challenge programme. It confirms, at minimum, the programme pattern of:

- Docker submission
- ROCm base image
- no outbound evaluation network
- no TCP service / no exposed port
- weights/dependencies shipped in-image
- hard resource/time gates
- GPU execution required

MC2 and MC3 use:

`rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`

The Match 4 repository now includes a **provisional** baseline Dockerfile using that image. It will not be tagged as final until the Match 4 kit confirms the exact contract.

## Critical unknowns blocking final image

- [ ] exact Match 4 grader invocation
- [ ] exact input schema
- [ ] exact output schema
- [ ] exact network topology / target-site delivery
- [ ] exact time budgets
- [ ] exact image-size and VRAM repetition for Match 4
- [ ] exact Match 4 sample/selfcheck
- [ ] LabLab Match 4 image submission field or equivalent route

## Final-image gates

Before marking READY:

- [ ] official Match 4 contract recovered
- [ ] thin grader adapter implemented
- [ ] official sample/selfcheck green
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
