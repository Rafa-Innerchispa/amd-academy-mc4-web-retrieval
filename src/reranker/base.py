from __future__ import annotations

from typing import Protocol, Sequence

from src.extractor.candidate_extractor import Candidate


class CandidateReranker(Protocol):
    """Optional local-only reranker for genuinely ambiguous candidate sets."""

    def rerank(
        self,
        *,
        query: str,
        candidates: Sequence[Candidate],
        page_text: str,
    ) -> list[Candidate]:
        """Return candidates in preferred order without inventing new values."""
        ...
