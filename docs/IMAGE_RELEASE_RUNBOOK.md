# Match 4 Image Release Runbook

This runbook exists so the final publication does not become a last-hour archaeology exercise.

## Current state

The repository contains a **provisional programme-level container baseline** derived from the official MC3 starter kit. It is not yet the final Match 4 image because the Match 4-specific grader interface is still unavailable publicly.

## Local baseline build

On the AMD host:

```bash
git checkout chatgpt/mc4-core-20261019
bash scripts/build_contract_baseline.sh
bash scripts/validate_contract_baseline.sh
```

Default local image:

```text
amd-academy-mc4-web-retrieval:contract-baseline
```

## When the official Match 4 kit appears

Before creating `mc4-final`:

1. compare its mandated `FROM` line with `docker/Dockerfile.contract-baseline`;
2. replace the provisional adapter with the exact official invocation contract;
3. copy the official selfcheck/sample harness into the validation flow;
4. freeze input/output JSON schema;
5. confirm whether targets are public internet or internal/sandbox hosts;
6. set private/internal host policy only as narrowly as the official grader requires;
7. run the full unit suite;
8. run the official selfcheck on the AMD R9700.

## Final image target

Planned URI:

```text
us-central1-docker.pkg.dev/innerops-agentic-platform/amd-academy-public/amd-academy-mc4-web-retrieval:mc4-final
```

Do not claim this URI exists until push and anonymous pull are proven.

## Required evidence before push

Capture:

- Git commit SHA
- Dockerfile hash
- official starter-kit/contract version
- AMD GPU model
- gfx target
- ROCm/PyTorch version
- unit-test result
- official sample/selfcheck result
- startup latency
- per-request p50/p95 if applicable
- whole-run time if applicable
- peak VRAM
- uncompressed image size
- network policy result

## Public registry verification

After push:

1. record the registry digest;
2. use a clean/anonymous Docker configuration;
3. pull the public URI without stored credentials;
4. run the official selfcheck from the anonymously pulled image;
5. run on AMD hardware again;
6. store the immutable digest in:
   - README
   - `docs/SUBMISSION_READINESS.md`
   - `docs/LABLAB_SUBMISSION.md`
   - umbrella repository Match 4 page.

## LabLab gate

Only mark **READY** when both conditions are true:

- the technical artifact is independently reproducible from the public image;
- LabLab exposes or documents the Match 4 submission route/field.

Until then, the status stays **ACTIVE DEVELOPMENT / NOT READY FOR FINAL SUBMISSION**.
