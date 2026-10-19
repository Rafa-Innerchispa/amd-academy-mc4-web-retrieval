# Public Match 4 Research Notes

Date: 2026-10-19

> **Status:** research only. Public competitor submissions are useful implementation clues, not the official AMD/LabLab grader contract.

## Current public convergence

Several published Match 4 entries independently converge on the same product shape:

- natural-language request
- optional starting URL
- one specific answer/value rather than a generic summary
- exact source URL
- bounded navigation
- structure-aware extraction
- refusal / empty result when evidence is missing
- AMD ROCm container execution
- local-model or deterministic fallback paths

Examples reviewed:

### WebScout Exact

https://lablab.ai/ai-hackathons/amd-lablab-ai-academy-challenge/vadym-bilobrovets/webscout-exact-match-4-retrieval-agent

Public description says it returns one exact value plus the source page, classifies answer types, uses bounded browsing, Qwen3-4B on AMD GPU with a rule fallback, and targets sub-30-second requests.

### Pinpoint

https://lablab.ai/ai-hackathons/amd-lablab-ai-academy-challenge/innova-ottawa/pinpoint-exact-web-answers-with-their-source

Public description says it uses anchor-aware navigation, clean text/JSON processing, a resident Qwen2.5-7B model, a 24-second internal budget, empty answers when unsupported, and describes a `python3 /app/app.py` / per-question output-file contract.

### WebRetriever

https://lablab.ai/ai-hackathons/amd-lablab-ai-academy-challenge/arcomega/webretriever-deterministic-web-retrieval-agent

Public description emphasizes a deterministic core, JSON-LD/tables, bounded multi-hop retrieval, source verification, and fail-closed refusal.

## What we adopt as engineering ideas

Our current Match 4 branch independently implements or prepares:

- exact typed values
- anchor-aware navigation
- tables + JSON-LD
- evidence verification
- fail-closed output
- bounded wall-clock execution
- provisional `/app/app.py`
- atomic output
- local-first ROCm container baseline

## What we do NOT treat as official

Until AMD/LabLab publishes the Match 4 starter kit, we do not freeze:

- exact CLI flags
- exact JSON keys
- exact output filename pattern
- exact target-site/network topology
- exact time budget
- exact model requirement, if any
- exact VRAM/image-size limits for Match 4

The official kit wins over every assumption in this document.


## Repository-level corroboration reviewed on 2026-10-19

The public repository `ctmakc/pinpoint-web-agent` adds stronger implementation evidence than the LabLab description alone:

- example invocation uses `python3 /app/app.py --query-id ... --url ... --query ...`
- writes `/app/output/<query-id>_output.json`
- accepts `--input`, `--output-dir`, and a compatibility `--index`
- uses the same ROCm 10 / PyTorch 2.13 / Python 3.14 base image already used by the programme baseline
- reports a resident model-server pattern and a 24-second internal request budget
- reports that the AMD notebook pool can restrict outbound sites, which makes seed-URL navigation important

This still does **not** make those details official. It does, however, increase confidence that our provisional adapter is pointed at the right interface family.

The public repository `dcain2336/amd-league-match4-webretriever` independently reinforces:

- deterministic intent parsing
- bounded multi-hop navigation
- JSON-LD and table extraction
- mandatory source grounding
- fail-closed behavior

## New implementation deltas informed by this review

The active branch now also includes:

- generic JSON/API response extraction, not only HTML and JSON-LD
- lexical-term relevance scoring instead of arbitrary substring matches
- redirect-domain lock tied to the original seed host
- bounded best-first navigation with backtracking after dead ends
- benchmark coverage for JSON APIs, prompt-injection decoys, and backtracking

These changes are engineering improvements, not claims about hidden grader behavior.
