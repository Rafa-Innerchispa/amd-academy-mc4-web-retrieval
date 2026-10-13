import re
from typing import Optional
from .models.schema import (
    RetrievalRequest,
    RetrievalResponse,
    VerificationStatus,
    NavigationStep,
)
from .config import AgentConfig, DEFAULT_CONFIG
from .parser.intent_parser import IntentParser
from .planner.navigation_planner import NavigationPlanner
from .browser.navigation_engine import NavigationEngine
from .extractor.dom_extractor import DOMExtractor
from .verifier.fail_closed_verifier import FailClosedVerifier
from .provenance.tracker import ProvenanceTracker

class WebRetrievalAgent:
    """
    End-to-End Autonomous Web Retrieval Agent.
    Operates strictly local-first with deterministic fail-closed verification.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.parser = IntentParser()
        self.browser = NavigationEngine(timeout=self.config.request_timeout_seconds)
        self.extractor = DOMExtractor()
        self.verifier = FailClosedVerifier(min_confidence=self.config.verification_threshold)
        self.provenance_tracker = ProvenanceTracker()

    def execute(self, request: RetrievalRequest) -> RetrievalResponse:
        intent = self.parser.parse(request.query, explicit_seed_url=request.seed_url)

        if not intent.inferred_seed_url:
            return RetrievalResponse(
                status="FAIL_CLOSED",
                query=request.query,
                verification_status=VerificationStatus.EVIDENCE_MISSING,
                failure_reason="No seed URL provided or inferred from query"
            )

        planner = NavigationPlanner(
            max_hops=request.max_hops or self.config.max_navigation_hops,
            lock_domain=not self.config.allow_external_domains
        )

        current_step = planner.get_initial_step(intent.inferred_seed_url)
        all_steps = [current_step]

        while current_step:
            # 1. Fetch Snapshot
            snapshot = self.browser.fetch(current_step.target_url)

            if snapshot.status_code != 200:
                # HTTP failure, attempt next navigation step or fail
                available_links = self.extractor.extract_links(snapshot.raw_html)
                current_step = planner.select_next_step(snapshot.url, available_links, intent)
                if current_step:
                    all_steps.append(current_step)
                continue

            # 2. Candidate Answer Extraction (Deterministic Heuristics / Local Pattern Match)
            candidate_answer = self._extract_candidate_answer(snapshot.cleaned_text, intent)

            if candidate_answer:
                # 3. Fail-Closed Verification
                status, provenance = self.verifier.verify(candidate_answer, snapshot)
                if status == VerificationStatus.VERIFIED and provenance:
                    self.provenance_tracker.log_record(provenance)
                    return RetrievalResponse(
                        status="SUCCESS",
                        query=request.query,
                        answer=candidate_answer,
                        verification_status=VerificationStatus.VERIFIED,
                        provenance=provenance,
                        navigation_trail=all_steps
                    )

            # 4. If answer not found or not verified on this page, plan next hop
            available_links = self.extractor.extract_links(snapshot.raw_html)
            current_step = planner.select_next_step(snapshot.url, available_links, intent)
            if current_step:
                all_steps.append(current_step)

        # 5. Fail-Closed Rejection when evidence could not be verified within bounded depth
        return RetrievalResponse(
            status="FAIL_CLOSED",
            query=request.query,
            verification_status=VerificationStatus.REJECTED_UNVERIFIED,
            navigation_trail=all_steps,
            failure_reason="CLAIM_NOT_FOUND_OR_UNVERIFIED_IN_EVIDENCE"
        )

    def _extract_candidate_answer(self, text: str, intent) -> Optional[str]:
        """
        Extracts candidate textual answers using structured pattern heuristics.
        """
        # Date heuristic
        if intent.target_attribute == "date_or_time":
            date_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
            match = re.search(date_pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
            iso_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', text)
            if iso_match:
                return iso_match.group(0)
            return None

        # Version heuristic
        if intent.target_attribute == "version":
            v_match = re.search(r'\b(?:v|version)?\s*(\d+\.\d+(?:\.\d+)?)\b', text, re.IGNORECASE)
            if v_match:
                return v_match.group(0)
            return None

        # Price heuristic
        if intent.target_attribute == "price":
            p_match = re.search(r'(?:\$|\bUSD\b)\s*[\d,]+(?:\.\d{2})?', text, re.IGNORECASE)
            if p_match:
                return p_match.group(0)
            return None

        # General keyword sentence extraction
        for kw in intent.keywords:
            pattern = re.compile(rf'([^.?!]*?\b{re.escape(kw)}\b[^.?!]*?[.?!])', re.IGNORECASE)
            s_match = pattern.search(text)
            if s_match:
                sentence = s_match.group(0).strip()
                if len(sentence) <= 300:
                    return sentence

        return None
