# Risk Register — AMD AI League Match 4

| Risk ID | Category | Description | Impact | Probability | Mitigation Strategy | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | Grader Unknowns | LabLab has not yet published the exact grader interface (CLI vs HTTP vs Docker stdin). | HIGH | HIGH | Modular design decoupling engine logic from I/O adapters; unified `src/agent.py` supports both CLI and API entrypoints. | MITIGATED |
| **RSK-02** | ROCm Memory Overflow | Local SLM inference exceeds VRAM limits on test worker. | HIGH | MEDIUM | Standardize on 3B/7B quantized models (INT4/INT8) and enforce strict CPU fallback path if HIP allocation fails. | MITIGATED |
| **RSK-03** | Runaway Navigation Loop | Agent loops endlessly across paginated or cyclical links. | HIGH | MEDIUM | Hardcoded max-hop ceiling ($N \le 5$), visited-URL set, and monotonic timeout budget (30s global). | MITIGATED |
| **RSK-04** | Hallucination / Bad Extraction | Model fabricates plausible numbers or dates not present on page. | CRITICAL | HIGH | Fail-closed verifier checks verbatim or high-confidence substring spans. Unmatched claims trigger fail-closed rejection. | MITIGATED |
| **RSK-05** | Dynamic Client JS | Target sites render content via heavy SPA React/Vue frameworks. | MEDIUM | HIGH | Architecture includes Playwright headless engine alongside fast static requests fallback. | MITIGATED |
| **RSK-06** | Bot Blocking / Rate Limiting | Websites return HTTP 403/429 during automated grading. | MEDIUM | MEDIUM | User-agent rotation, polite crawl delay, and local snapshot caching. | MITIGATED |
