import time
from typing import Optional
from urllib.parse import urlparse

from .browser.navigation_engine import NavigationEngine
from .config import AgentConfig, DEFAULT_CONFIG
from .extractor.candidate_extractor import CandidateExtractor
from .extractor.dom_extractor import DOMExtractor
from .models.schema import RetrievalRequest, RetrievalResponse, VerificationStatus
from .parser.intent_parser import IntentParser
from .planner.navigation_planner import NavigationPlanner
from .provenance.tracker import ProvenanceTracker
from .reranker.base import CandidateReranker
from .search.search_engine import SearchEngine
from .verifier.fail_closed_verifier import FailClosedVerifier


class WebRetrievalAgent:
    """Bounded web-retrieval agent with deterministic grounding.

    The core intentionally avoids free-form answer synthesis. Candidate values are
    extracted from the fetched page, ranked against the request, then accepted
    only when the exact value can be grounded back to the same page snapshot.
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        reranker: Optional[CandidateReranker] = None,
    ):
        self.config = config or DEFAULT_CONFIG
        self.reranker = reranker
        self.parser = IntentParser()
        self.browser = NavigationEngine(
            timeout=self.config.request_timeout_seconds,
            user_agent=self.config.user_agent,
            allow_private_network_targets=self.config.allow_private_network_targets,
            allowed_private_hosts=self.config.allowed_private_hosts,
        )
        self.extractor = DOMExtractor()
        self.candidates = CandidateExtractor()
        self.verifier = FailClosedVerifier(
            min_confidence=self.config.verification_threshold
        )
        self.provenance_tracker = ProvenanceTracker()
        self.search = SearchEngine(
            endpoint=self.config.search_endpoint,
            timeout_seconds=self.config.search_timeout_seconds,
            max_results=self.config.search_max_results,
        )

    def _candidate_identity(self, value: str, attribute: str) -> str:
        normalized = " ".join(str(value).strip().lower().split())
        if attribute == "price":
            normalized = normalized.replace("us$", "").replace("usd", "").replace("$", "")
            normalized = normalized.replace(",", "").replace(" ", "")
        elif attribute in {"technical_spec", "percentage", "duration"}:
            normalized = normalized.replace(" ", "").replace("–", "-")
        return normalized.strip()

    def execute(self, request: RetrievalRequest) -> RetrievalResponse:
        started = time.monotonic()
        deadline = started + self.config.total_budget_seconds
        intent = self.parser.parse(request.query, explicit_seed_url=request.seed_url)

        search_used = False
        if not intent.inferred_seed_url:
            if not self.config.enable_public_search:
                return RetrievalResponse(
                    status="FAIL_CLOSED",
                    query=request.query,
                    verification_status=VerificationStatus.EVIDENCE_MISSING,
                    failure_reason="NO_SEED_URL",
                )

            remaining_search_budget = deadline - time.monotonic()
            if remaining_search_budget <= 0:
                return RetrievalResponse(
                    status="FAIL_CLOSED",
                    query=request.query,
                    verification_status=VerificationStatus.REJECTED_UNVERIFIED,
                    failure_reason="TIME_BUDGET_EXCEEDED",
                    metadata={
                        "elapsed_seconds": round(time.monotonic() - started, 3),
                    },
                )

            search_results = self.search.search(
                request.query,
                timeout_seconds=remaining_search_budget,
            )
            if time.monotonic() >= deadline:
                return RetrievalResponse(
                    status="FAIL_CLOSED",
                    query=request.query,
                    verification_status=VerificationStatus.REJECTED_UNVERIFIED,
                    failure_reason="TIME_BUDGET_EXCEEDED",
                    metadata={
                        "elapsed_seconds": round(time.monotonic() - started, 3),
                    },
                )

            if not search_results:
                return RetrievalResponse(
                    status="FAIL_CLOSED",
                    query=request.query,
                    verification_status=VerificationStatus.EVIDENCE_MISSING,
                    failure_reason="SEARCH_NO_RESULTS",
                )

            intent.inferred_seed_url = search_results[0].url
            search_used = True

        planner = NavigationPlanner(
            max_hops=request.max_hops or self.config.max_navigation_hops,
            lock_domain=not self.config.allow_external_domains,
        )

        current_step = planner.get_initial_step(intent.inferred_seed_url)
        all_steps = [current_step]
        seed_host = (
            (urlparse(intent.inferred_seed_url).hostname or "").rstrip(".").lower()
        )

        while current_step:
            if time.monotonic() - started >= self.config.total_budget_seconds:
                return RetrievalResponse(
                    status="FAIL_CLOSED",
                    query=request.query,
                    verification_status=VerificationStatus.REJECTED_UNVERIFIED,
                    navigation_trail=all_steps,
                    failure_reason="TIME_BUDGET_EXCEEDED",
                    metadata={
                        "elapsed_seconds": round(time.monotonic() - started, 3),
                    },
                )

            snapshot = self.browser.fetch(
                current_step.target_url,
                allowed_host=None if self.config.allow_external_domains else seed_host,
                deadline_monotonic=deadline,
            )

            if snapshot.status_code == 504 or time.monotonic() >= deadline:
                return RetrievalResponse(
                    status="FAIL_CLOSED",
                    query=request.query,
                    verification_status=VerificationStatus.REJECTED_UNVERIFIED,
                    navigation_trail=all_steps,
                    failure_reason="TIME_BUDGET_EXCEEDED",
                    metadata={
                        "elapsed_seconds": round(time.monotonic() - started, 3),
                    },
                )

            if snapshot.status_code == 200:
                ranked = self.candidates.extract(
                    snapshot.raw_html,
                    snapshot.cleaned_text,
                    intent,
                )

                reranker_used = False
                ambiguity_detected = False
                candidate_window = ranked[: self.config.max_candidates_per_page]
                if len(candidate_window) >= 2:
                    top = candidate_window[0]
                    top_identity = self._candidate_identity(top.value, intent.target_attribute)
                    competitor = next(
                        (
                            item
                            for item in candidate_window[1:]
                            if self._candidate_identity(item.value, intent.target_attribute)
                            != top_identity
                        ),
                        None,
                    )
                    ambiguity_detected = (
                        competitor is not None
                        and abs(top.score - competitor.score)
                        <= self.config.reranker_margin_threshold
                    )
                    if ambiguity_detected and self.reranker is not None:
                        reranked = self.reranker.rerank(
                            query=request.query,
                            candidates=candidate_window,
                            page_text=snapshot.cleaned_text,
                        )
                        if reranked:
                            candidate_window = list(reranked)[: self.config.max_candidates_per_page]
                            reranker_used = True

                for candidate in candidate_window:
                    if candidate.score < self.config.min_candidate_score:
                        continue
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
                                "elapsed_seconds": round(time.monotonic() - started, 3),
                                "search_used": search_used,
                                "ambiguity_detected": ambiguity_detected,
                                "reranker_used": reranker_used,
                            },
                        )

            available_links = self.extractor.extract_link_candidates(snapshot.raw_html)
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
            metadata={
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "search_used": search_used,
            },
        )
