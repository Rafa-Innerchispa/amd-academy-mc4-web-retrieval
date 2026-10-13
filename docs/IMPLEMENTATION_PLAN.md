# Implementation Plan & Backlog — AMD AI League Match 4

## Prioritized Milestone Backlog

### Phase 1: Invariant Foundations & Independent Scaffold (COMPLETED)
- [x] Create standalone git repository `amd-academy-mc4-web-retrieval`.
- [x] Complete contract documentation with Facts vs Assumptions vs Pending Releases.
- [x] Complete system architecture specification with AMD ROCm focus.
- [x] Complete risk register and mitigation matrix.
- [x] Implement core data schemas (`RetrievalRequest`, `DOMSnapshot`, `ProvenanceRecord`).
- [x] Implement deterministic Intent Parser with entity and attribute recognition.
- [x] Implement Bounded Navigation Planner with cycle detection.
- [x] Implement DOM Content Extractor with table parsing and boilerplate pruning.
- [x] Implement Fail-Closed Anti-Hallucination Verifier.
- [x] Implement Provenance & Cryptographic Audit Logger.
- [x] Implement complete unit and integration test suite passing 100%.

### Phase 2: Live Browser Integration & Headless Rendering (P1)
- [ ] Implement optional Playwright headless chromium wrapper for client-rendered JavaScript.
- [ ] Add semantic embedding ranking for intra-site link selection.
- [ ] Add robust table-to-dataframe serialization for complex financial/tabular queries.

### Phase 3: AMD ROCm SLM Integration (P1)
- [ ] Package ROCm inference loader (Llama-3.2-3B-Instruct / Qwen2.5-Coder-7B).
- [ ] Integrate llama.cpp HIP bindings with fallback to GGUF CPU.
- [ ] Add memory-bound context pruning for long DOM extraction.

### Phase 4: Grader Binding (Trigger: Upon Official LabLab Release) (P0)
- [ ] Update `CHALLENGE_CONTRACT.md` with official benchmark rules.
- [ ] Implement official grader entrypoint (CLI or REST API).
- [ ] Build submission Docker container based on official AMD ROCm base image.

### Phase 5: End-to-End Benchmark & Submission (P0)
- [ ] Run benchmark evaluation across challenge validation set.
- [ ] Package final demo video and submission README.
