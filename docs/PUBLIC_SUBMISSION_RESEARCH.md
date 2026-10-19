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
