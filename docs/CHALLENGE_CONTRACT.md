# Official Challenge Contract — AMD AI League Match 4

## 1. Challenge Metadata & Canonical Sources
* **Competition:** AMD AI League (LabLab.ai)
* **Milestone:** Match 4 — Intelligent Web Information Retrieval
* **Active Window:** October 13, 2026 – October 27, 2026
* **Reward:** 1,800 Points
* **Official Portal:** [LabLab.ai AMD AI League](https://lablab.ai/event/amd)
* **AMD Playbooks Reference:** [github.com/amd/playbooks](https://github.com/amd/playbooks)
* **AMD Skills Reference:** [github.com/amd/skills](https://github.com/amd/skills)

---

## 2. Rigorous Fact, Assumption & Pending Releases Separation

### A. CONFIRMED FACTS (Publicly Published)
1. **Challenge Name:** Match 4: Intelligent Web Information Retrieval.
2. **Timeline:** October 13 – October 27, 2026.
3. **Point Value:** 1,800 points.
4. **Stated Mission:** *"Build an AI agent that can navigate websites, understand a natural-language request and accurately retrieve the specific information a user needs."*
5. **Compute & Technology Stack:** Hosted on AMD infrastructure (AMD Developer Cloud / ROCm), requiring workloads compatible with AMD GPUs.
6. **Cost Model:** Strictly local-first execution. Zero dependence on paid external LLM APIs.

### B. ARCHITECTURAL ASSUMPTIONS (Engineered Best Practices)
1. **Input Interface:** The agent accepts a user request containing:
   - A natural language question or target retrieval specification.
   - An optional or inferred initial URL / seed domain.
2. **Navigation Complexity:** Retrieval tasks will test:
   - Direct single-page extraction.
   - Multi-step intra-site navigation (following links, paging, searching).
   - Tabular and structured list parsing.
3. **Execution Guardrails:** Autonomous loops must be strictly bounded ($N \le 5$ navigation hops, max 30s per fetch) to prevent hanging during grading.
4. **Ground Truth Validation:** Graders in automated AI benchmarks compare extracted values against exact ground truth; therefore, strict text grounding and verbatim span extraction is prioritized over generative summarization.
5. **Local Inference Engine:** AMD ROCm PyTorch / HIP inference using small instruction models (Llama-3.2-3B-Instruct, Qwen2.5-Coder-7B-Instruct) quantized in INT4/INT8 to fit within 8GB–16GB VRAM bounds.

### C. PENDING LABLAB RELEASES (Awaiting Official Grader Brief)
The following specifications remain unreleased as of October 13, 2026 (status: "Coming soon"):
1. **Grader Protocol / Entrypoint:** Whether the grader will invoke a CLI command (`python agent.py --input in.json --output out.json`), a REST API container (`POST /retrieve`), or an interactive web UI.
2. **Official Dataset / Domains:** Whether targets are live internet sites or offline mocked sandboxes.
3. **Official Base Docker Image:** Exact ROCm version (`rocm/pytorch:rocm6.2_ubuntu22.04` or similar).
4. **Scoring Breakdown:** Exact weighting between:
   - Accuracy / Exact Match (EM) & F1 Score.
   - Provenance / Citation fidelity.
   - Retrieval Latency & Step Count.

> **Policy on Unknowns:** Under no circumstances shall this codebase hardcode unreleased grader constraints as facts. All integrations with the grader are isolated behind an adapter pattern (`src/agent.py` and `src/cli.py`) for rapid adaptation once the brief drops.

---

## 3. Requirement Traceability Matrix

| Official Requirement | Implementation Component | Test Suite | Evidence Artifact |
| :--- | :--- | :--- | :--- |
| **Natural Language Request Understanding** | `src/parser/intent_parser.py` | `tests/test_parser.py` | Structured `ParsedIntent` JSON with entities, targets, and constraints |
| **Website Navigation & Link Traversal** | `src/planner/navigation_planner.py`, `src/browser/navigation_engine.py` | `tests/test_planner.py` | `NavigationStep` trail with loop prevention and bounded hops |
| **DOM & Content Extraction** | `src/extractor/dom_extractor.py` | `tests/test_extractor.py` | Clean markdown DOM text and structured table key-value pairs |
| **Accurate Information Retrieval** | `src/agent.py` | `tests/test_agent_e2e.py` | Verbatim text answer matching target query criteria |
| **Anti-Hallucination & Fail-Closed** | `src/verifier/fail_closed_verifier.py` | `tests/test_fail_closed.py` | Rejection response with `UNVERIFIABLE_CLAIM` when ground truth missing |
| **Citation & Provenance** | `src/provenance/tracker.py` | `tests/test_provenance.py` | `ProvenanceRecord` containing SHA-256 snapshot hashes and offsets |
| **Local-First AMD/ROCm Stack** | `src/config.py`, ROCm runtime | Unit & Mock harnesses | Zero external API calls verified in test logs |
