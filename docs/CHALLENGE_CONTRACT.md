# AMD AI League Match 4 — Challenge Contract

Last reviewed: 2026-10-19

## Canonical public source

AMD AI League on LabLab:

- Match 4: **Intelligent Web Information Retrieval**
- Active window: **October 13–27, 2026**
- Points: **1,800**
- Public mission: **build an AI agent that can navigate websites, understand a natural-language request and accurately retrieve the specific information a user needs**
- Match 4 is marked **Live now**
- LabLab states that participants do not need their own AMD hardware or cloud credits; the hackathon notebook environment provides AMD GPU infrastructure.

Public League page:
https://lablab.ai/ai-hackathons/amd-lablab-ai-academy-challenge

## Live LabLab submission-form check — 2026-10-19

An authenticated read of the team's current LabLab submission form shows Step 1 exposing exactly these challenge-artifact fields:

- `Mini Challenge 2 Image`
- `Mini Challenge 3 Image`

There is **no visible Mini Challenge 4 Image field** in the current form at the time of this check.

This is evidence about the present UI only. It does not prove that Match 4 will never use this form or that a separate publication route will not appear. The final Match 4 image should therefore be prepared independently and held ready for the moment LabLab exposes or documents the submission mechanism.

## Important release-state finding

As of this review, the public League page exposes a working Match 3 starter-kit link, but the visible **View match details** control for Match 4 does not expose a usable destination or downloadable starter kit from the public page.

Therefore the following are **not yet treated as confirmed official facts in this repository**:

- exact Match 4 grader entrypoint
- exact input JSON schema
- exact output JSON schema
- mandatory Docker base image
- network policy during grading
- startup / per-query / total runtime budgets
- GPU VRAM bounds
- maximum image size
- whether the grader supplies a seed URL, a search query, or both
- whether JavaScript rendering/headless Chromium is available or required
- exact submission field for the Match 4 image in LabLab

The repository keeps the internal retrieval core isolated from the future grader adapter so these details can be wired in without rewriting the engine.

## Confirmed requirements mapped to implementation

| Public requirement | Current implementation |
| --- | --- |
| Understand natural-language request | `src/parser/intent_parser.py` |
| Navigate websites | `src/planner/navigation_planner.py`, `src/browser/navigation_engine.py` |
| Retrieve specific information accurately | `src/extractor/candidate_extractor.py` |
| Ground answer in fetched evidence | `src/verifier/fail_closed_verifier.py` |
| Keep provenance | `src/provenance/tracker.py` |
| Bounded autonomous behavior | hop budget + loop prevention |
| Safe web access | public-address URL policy + redirect revalidation |
| Product/demo usability | isolated `demo/` presentation layer |

## Engineering assumptions, not official rules

Until the official Match 4 grader brief or starter kit is available, these remain design choices:

- a seed URL may be supplied with the query
- one exact value is preferable to a generic summary
- source URL/provenance should accompany the value
- unsupported answers should fail closed
- tables and JSON-LD are useful structured sources
- navigation should stay bounded
- page content must be treated as untrusted data
- private/loopback/link-local network destinations must be blocked

These choices are deliberately conservative and easy to adapt.

## Public competitor observations

Public Match 4 submissions visible on LabLab already describe Dockerized retrieval agents with exact-value answers, source URLs, bounded navigation, local AMD/ROCm inference or deterministic extraction, and fail-closed behavior.

Those submissions are useful evidence that the implementation direction is reasonable, but they are **not authoritative challenge specifications** and are not used here to invent grader rules.

## Submission gate

Do **not** mark Match 4 READY until all of these exist:

- official/current grader contract recovered
- grader adapter implemented
- full unit and held-out tests green
- official starter-kit/sample run green if/when released
- Docker image built on AMD-compatible runtime
- public registry image
- anonymous pull verified
- public pulled image re-run
- immutable digest recorded
- exact LabLab submission route confirmed

## Separation from the demo UI

The `demo/` UI is a presentation and product-use layer only.

The future graded container must remain minimal and must not depend on the demo UI unless the official grader explicitly requires a web interface.


## Programme-level evidence from the official MC3 starter kit

The user-provided official MC3 starter kit states that the container rules are the same for every challenge in the programme. It also confirms that MC2 and MC3 use the same ROCm base, the same image-size/VRAM rules, and the same no-server/no-port container shape.

This is strong evidence for preparing the Match 4 container baseline now, while still keeping the Match 4-specific grader invocation and output schema unfrozen.

One important consequence is network topology: MC3 evaluation has no outbound network. Match 4 is a web-navigation task, so the official Match 4 kit may provide websites through an internal/sandbox network rather than the public internet. The retrieval engine therefore blocks private targets by default but supports an explicit allowlist for grader-provided internal hosts. We will not enable broad private-network access unless the official Match 4 contract requires it.

See `docs/MC3_STARTER_KIT_LESSONS.md`.
