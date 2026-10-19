from typing import List, Set, Optional, Tuple
from urllib.parse import urlparse, urljoin

from ..models.schema import NavigationStep, ParsedIntent


class NavigationPlanner:
    """Bounded best-first navigation with loop prevention and domain locking.

    Candidate links are retained in a small frontier. If the highest-ranked
    link is a dead end, the planner can return to an earlier alternative
    instead of terminating the whole retrieval.
    """

    def __init__(
        self,
        max_hops: int = 5,
        lock_domain: bool = True,
        max_frontier: int = 64,
    ):
        self.max_hops = max_hops
        self.lock_domain = lock_domain
        self.max_frontier = max_frontier
        self.visited_urls: Set[str] = set()
        self.navigation_trail: List[NavigationStep] = []
        self.seed_domain: str = ""
        self._queued_urls: Set[str] = set()
        self._frontier: List[Tuple[float, int, str, str]] = []
        self._sequence = 0

    def get_initial_step(self, seed_url: str) -> NavigationStep:
        parsed_seed = urlparse(seed_url)
        self.seed_domain = (parsed_seed.hostname or "").rstrip(".").lower()
        step = NavigationStep(
            step_number=1,
            action="VISIT_URL",
            target_url=seed_url,
            reason="Starting seed URL navigation",
        )
        self.visited_urls.add(seed_url)
        self.navigation_trail.append(step)
        return step

    def select_next_step(
        self,
        current_url: str,
        available_links: List[str],
        intent: ParsedIntent,
    ) -> Optional[NavigationStep]:
        self._add_to_frontier(current_url, available_links, intent)
        return self._pop_next_step()

    def _add_to_frontier(
        self,
        current_url: str,
        available_links: List[str],
        intent: ParsedIntent,
    ) -> None:
        for raw_link in available_links:
            if isinstance(raw_link, (tuple, list)):
                href = raw_link[0]
                anchor_text = raw_link[1] if len(raw_link) > 1 else ""
            else:
                href = raw_link
                anchor_text = ""

            resolved_link = urljoin(current_url, href)
            parsed_resolved = urlparse(resolved_link)

            resolved_domain = (parsed_resolved.hostname or "").rstrip(".").lower()
            if self.lock_domain and resolved_domain and resolved_domain != self.seed_domain:
                continue

            if resolved_link in self.visited_urls or resolved_link in self._queued_urls:
                continue

            score = self._score_link(resolved_link, str(anchor_text), intent)
            reason = (
                f"Best-first relevance score {score:.2f}"
                if score > 0
                else "Bounded exploratory navigation"
            )
            self._sequence += 1
            self._frontier.append((score, self._sequence, resolved_link, reason))
            self._queued_urls.add(resolved_link)

        # Keep the frontier bounded. Higher scores win; for equal scores,
        # earlier discovery wins so behavior remains deterministic.
        self._frontier.sort(key=lambda item: (-item[0], item[1]))
        if len(self._frontier) > self.max_frontier:
            removed = self._frontier[self.max_frontier :]
            self._frontier = self._frontier[: self.max_frontier]
            for _score, _seq, url, _reason in removed:
                self._queued_urls.discard(url)

    def _pop_next_step(self) -> Optional[NavigationStep]:
        if len(self.navigation_trail) >= self.max_hops:
            return None

        while self._frontier:
            _score, _seq, best_link, reason = self._frontier.pop(0)
            self._queued_urls.discard(best_link)
            if best_link in self.visited_urls:
                continue

            next_step = NavigationStep(
                step_number=len(self.navigation_trail) + 1,
                action="FOLLOW_LINK",
                target_url=best_link,
                reason=reason,
            )
            self.visited_urls.add(best_link)
            self.navigation_trail.append(next_step)
            return next_step
        return None

    def _score_link(self, resolved_link: str, anchor_text: str, intent: ParsedIntent) -> float:
        score = 0.0
        haystack_url = resolved_link.lower()
        haystack_anchor = anchor_text.lower()

        for kw in intent.keywords:
            keyword = kw.lower()
            if keyword in haystack_url:
                score += 1.0
            if keyword in haystack_anchor:
                score += 2.0

        pagination_terms = ("next", "next page", "more results", "more", "older")
        if any(term == haystack_anchor.strip() for term in pagination_terms):
            score += 0.75
        if "page=" in haystack_url or "/page/" in haystack_url:
            score += 0.5
        return score
