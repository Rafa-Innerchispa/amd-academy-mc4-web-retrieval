from difflib import SequenceMatcher
from typing import Tuple, Optional
from ..models.schema import VerificationStatus, ProvenanceRecord, DOMSnapshot

class FailClosedVerifier:
    """
    Anti-hallucination verification engine.
    Ensures that every candidate answer is physically groundable in the DOM snapshot.
    If the evidence is absent, fails closed.
    """

    def __init__(self, min_confidence: float = 0.85):
        self.min_confidence = min_confidence

    def verify(self, candidate_answer: str, snapshot: DOMSnapshot) -> Tuple[VerificationStatus, Optional[ProvenanceRecord]]:
        if not candidate_answer or not candidate_answer.strip():
            return VerificationStatus.EVIDENCE_MISSING, None

        normalized_answer = candidate_answer.strip().lower()
        cleaned_text = snapshot.cleaned_text
        normalized_dom = cleaned_text.lower()

        # Step 1: Check Exact Substring Grounding
        exact_idx = normalized_dom.find(normalized_answer)
        if exact_idx != -1:
            verbatim_excerpt = cleaned_text[exact_idx:exact_idx + len(candidate_answer)]
            provenance = ProvenanceRecord(
                snapshot_hash=snapshot.content_hash,
                source_url=snapshot.url,
                char_offset_start=exact_idx,
                char_offset_end=exact_idx + len(candidate_answer),
                verbatim_text=verbatim_excerpt,
                timestamp_utc=snapshot.timestamp_utc
            )
            return VerificationStatus.VERIFIED, provenance

        # Step 2: Bounded Fuzzy Matching for near-exact spans (e.g. minor whitespace discrepancies)
        words = candidate_answer.split()
        if len(words) >= 3:
            first_three = " ".join(words[:3]).lower()
            idx = normalized_dom.find(first_three)
            if idx != -1:
                candidate_span = cleaned_text[idx:idx + len(candidate_answer) + 20]
                ratio = SequenceMatcher(None, candidate_answer.lower(), candidate_span.lower()).ratio()
                if ratio >= self.min_confidence:
                    provenance = ProvenanceRecord(
                        snapshot_hash=snapshot.content_hash,
                        source_url=snapshot.url,
                        char_offset_start=idx,
                        char_offset_end=idx + len(candidate_span),
                        verbatim_text=candidate_span,
                        timestamp_utc=snapshot.timestamp_utc
                    )
                    return VerificationStatus.VERIFIED, provenance

        # Step 3: Raw HTML grounding for structured data such as JSON-LD.
        normalized_raw = snapshot.raw_html.lower()
        raw_idx = normalized_raw.find(normalized_answer)
        if raw_idx != -1:
            verbatim_excerpt = snapshot.raw_html[
                raw_idx:raw_idx + len(candidate_answer)
            ]
            provenance = ProvenanceRecord(
                snapshot_hash=snapshot.content_hash,
                source_url=snapshot.url,
                char_offset_start=raw_idx,
                char_offset_end=raw_idx + len(candidate_answer),
                verbatim_text=verbatim_excerpt,
                timestamp_utc=snapshot.timestamp_utc,
                coordinate_space="raw_html",
            )
            return VerificationStatus.VERIFIED, provenance

        # Step 4: FAIL-CLOSED REJECTION
        return VerificationStatus.REJECTED_UNVERIFIED, None
