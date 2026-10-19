from typing import Optional

from .browser.navigation_engine import NavigationEngine
from .config import AgentConfig, DEFAULT_CONFIG
from .extractor.candidate_extractor import CandidateExtractor
from .extractor.dom_extractor import DOMExtractor
from .models.schema import RetrievalRequest, RetrievalResponse, VerificationStatus
from .parser.intent_parser import IntentParser
from .planner.navigation_planner import NavigationPlanner
from .provenance.tracker import ProvenanceTracker
from .verifier.fail_closed_verifier import FailClosedVerifier


class WebRetrievalAgent:
    """Bounded web-retrieval agent with deterministic grounding.

    The core intentionally avoids free-form answer synthesis. Candidate values are
    extracted from the fetched page, ranked against the request, then accepted
    only when the exact value can be grounded back to the same page snapshot.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.parser = IntentParser()
        self.browser = NavigationEngine(
            timeout=self.config.request_timeout_seconds,
            user_agent=self.config.user_agent,
        )
        self.extractor = DOMExtractor()
        self.candidates = CandidateExtractor()
        self.verifier = FailClosedVerifier(
            min_confidence=self.config.verification_threshold
        )
        self.provenance_tracker = ProvenanceTracker()

    def execute(self, request: RetrievalRequest) -> RetrievalResponse:
        intent = self.parser.parse(request.query, explicit_seed_url=request.seed_url)

        if not intent.inferred_seed_url:
            return RetrievalResponse(
                status="FAIL_CLOSED",
                query=request.query,
                verification_status=VerificationStatus.EVIDENCE_MISSING,
                failure_reason="NO_SEED_URL",
            )

        planner = NavigationPlanner(
            max_hops=request.max_hops or self.config.max_navigation_hops,
            lock_domain=not self.config.allow_external_domains,
        )

        current_step = planner.get_initial_step(intent.inferred_seed_url)
        all_steps = [current_step]

        while current_step:
            snapshot = self.browser.fetch(current_step.target_url)

            if snapshot.status_code == 200:
                ranked = self.candidates.extract(
                    snapshot.raw_html,
                    snapshot.cleaned_text,
                    intent,
                )

                for candidate in ranked[: self.config.max_candidates_per_page]:
                    status, provenance = self.verifier.verify(
                        candidate.value,
                        snapshot,
                    )
                    if status == VerificationStatus.VERIFIED and provenance:
                        self.provenance_tracker.log_record(provenance)
                        return RetrievalResponse(
                            status="SUCCESS",
                            query=request.query,
                            answer=candidate.value,
                            verification_status=VerificationStatus.VERIFIED,
                            provenance=provenance,
                            navigation_trail=all_steps,
                            metadata={
                                "candidate_source_kind": candidate.source_kind,
                                "candidate_score": round(candidate.score, 3),
                            },
                        )

            available_links = self.extractor.extract_links(snapshot.raw_html)
            current_step = planner.select_next_step(
                snapshot.url,
                available_links,
                intent,
            )
            if current_step:
                all_steps.append(current_step)

        return RetrievalResponse(
            status="FAIL_CLOSED",
            query=request.query,
            verification_status=VerificationStatus.REJECTED_UNVERIFIED,
            navigation_trail=all_steps,
            failure_reason="CLAIM_NOT_FOUND_OR_UNVERIFIED_IN_EVIDENCE",
        )
