# AMD AI League — Match 4: Intelligent Web Information Retrieval
**Repository:** `amd-academy-mc4-web-retrieval`  
**Milestone:** AMD AI League Match 4 (Oct 13 – Oct 27, 2026 | 1,800 pts)  
**Execution Environment:** Local-first on AMD Hardware & ROCm (Zero Paid External APIs)  
**Target Architecture:** Autonomous Web Retrieval Agent with Fail-Closed Anti-Hallucination & Provenance Guarantee

---

## 1. Overview & Challenge Objective
As published by the official AMD AI League on LabLab.ai:
> *"Build an AI agent that can navigate websites, understand a natural-language request and accurately retrieve the specific information a user needs."*

This repository houses an independent, production-grade scaffold designed from first principles for Match 4. It operates strictly **local-first** on AMD ROCm compute, decoupling the navigation and reasoning logic from external commercial APIs.

---

## 2. Core Pillars

1. **Local-First AMD/ROCm Acceleration**:
   - Model inference powered by local Small Language Models (e.g. Llama-3.2-3B, Qwen2.5-Coder-7B) running via ROCm / HIP / llama.cpp-hip / vLLM-rocm.
   - Zero dependency on external paid API endpoints (OpenAI, Anthropic, Google).
2. **Deterministic & Bounded Navigation**:
   - Bounded hops ($N \le 5$) with loop detection, domain restrictions, and strict execution timeouts.
   - Safe HTTP / headless browser abstraction with DOM distillation.
3. **Fail-Closed Anti-Hallucination Engine**:
   - Every extracted claim or datum must be grounded in an exact or high-confidence fuzzy match against the snapshot DOM.
   - If evidence is absent, the agent fails closed (`UNVERIFIABLE_CLAIM` / `NOT_FOUND`), refusing to generate unbacked assumptions.
4. **Cryptographic Provenance & Evidence Audit**:
   - Every retrieved fact is stamped with the SHA-256 checksum of the rendered DOM snapshot, URL, timestamp, and character offset coordinates.
5. **Strict Architectural Isolation**:
   - Entirely standalone repository. Zero dependencies or couplings with prior milestone modules (MC3, ACT III, InnerOS).

---

## 3. Directory Structure
```text
amd-academy-mc4-web-retrieval/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── docs/
│   ├── CHALLENGE_CONTRACT.md    # Official links, Facts vs Assumptions vs Pending Releases
│   ├── ARCHITECTURE.md          # ROCm local-first agent design & data flow
│   ├── RISK_REGISTER.md         # Technical, model, and grader risks with mitigations
│   └── IMPLEMENTATION_PLAN.md   # Prioritized backlog (P0-P3) & roadmap
├── src/
│   ├── __init__.py
│   ├── config.py                # Agent configuration and resource bounds
│   ├── agent.py                 # Core WebRetrievalAgent orchestrator
│   ├── cli.py                   # Command-line interface
│   ├── models/
│   │   ├── __init__.py
│   │   └── schema.py            # Pydantic schemas (Request, Response, Evidence, etc.)
│   ├── parser/
│   │   ├── __init__.py
│   │   └── intent_parser.py     # NL Intent Parsing & constraint extraction
│   ├── planner/
│   │   ├── __init__.py
│   │   └── navigation_planner.py# Bounded navigation state machine
│   ├── browser/
│   │   ├── __init__.py
│   │   └── navigation_engine.py # HTTP/headless browser client with retry bounds
│   ├── extractor/
│   │   ├── __init__.py
│   │   └── dom_extractor.py     # Boilerplate stripper & markdown/table extraction
│   ├── verifier/
│   │   ├── __init__.py
│   │   └── fail_closed_verifier.py # Anti-hallucination grounding verification
│   └── provenance/
│       ├── __init__.py
│       └── tracker.py           # SHA-256 evidence logging & provenance records
└── tests/
    ├── test_parser.py
    ├── test_planner.py
    ├── test_extractor.py
    ├── test_fail_closed.py
    ├── test_provenance.py
    └── test_agent_e2e.py
```

---

## 4. Quickstart

### Prerequisites
- Python 3.10+
- PyTorch with ROCm support (for GPU acceleration on AMD Radeon/Instinct) or standard CPU fallback
- Linux / WSL2 environment

### Installation
```bash
git clone https://github.com/Rafa-Innerchispa/amd-academy-mc4-web-retrieval.git
cd amd-academy-mc4-web-retrieval
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running Tests
Execute the full verification test suite:
```bash
pytest -v tests/
```

### Running the CLI
```bash
python3 -m src.cli --query "What is the release date of ROCm 6.2?" --url "https://rocm.docs.amd.com"
```

---

## 5. Official Requirement Traceability
See [CHALLENGE_CONTRACT.md](docs/CHALLENGE_CONTRACT.md) for the complete facts, assumptions, pending releases, and the requirement traceability matrix.
