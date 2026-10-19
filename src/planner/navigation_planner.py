from typing import List, Set, Optional
from urllib.parse import urlparse, urljoin
from ..models.schema import NavigationStep, ParsedIntent

class NavigationPlanner:
    """
    Bounded navigation state machine with loop prevention and domain locking.
    """

    def __init__(self, max_hops: int = 5, lock_domain: bool = True):
        self.max_hops = max_hops
        self.lock_domain = lock_domain
        self.visited_urls: Set[str] = set()
        self.navigation_trail: List[NavigationStep] = []

    def get_initial_step(self, seed_url: str) -> NavigationStep:
        step = NavigationStep(
            step_number=1,
            action="VISIT_URL",
            target_url=seed_url,
            reason="Starting seed URL navigation"
        )
        self.visited_urls.add(seed_url)
        self.navigation_trail.append(step)
        return step

    def select_next_step(self, current_url: str, available_links: List[str], intent: ParsedIntent) -> Optional[NavigationStep]:
        if len(self.navigation_trail) >= self.max_hops:
            return None

        current_domain = urlparse(current_url).netloc

        scored_links = []
        for raw_link in available_links:
            if isinstance(raw_link, (tuple, list)):
                href = raw_link[0]
                anchor_text = raw_link[1] if len(raw_link) > 1 else ""
            else:
                href = raw_link
                anchor_text = ""

            resolved_link = urljoin(current_url, href)
            parsed_resolved = urlparse(resolved_link)

            # Domain lock validation
            if self.lock_domain and parsed_resolved.netloc and parsed_resolved.netloc != current_domain:
                continue

            # Loop prevention
            if resolved_link in self.visited_urls:
                continue

            # Score both URL and visible anchor text. Real sites often use
            # opaque paths while the human-readable anchor carries the clue.
            score = 0
            haystack_url = resolved_link.lower()
            haystack_anchor = str(anchor_text).lower()
            for kw in intent.keywords:
                if kw in haystack_url:
                    score += 1
                if kw in haystack_anchor:
                    score += 2
            
            scored_links.append((score, resolved_link))

        if not scored_links:
            return None

        # Sort descending by relevance score
        scored_links.sort(key=lambda x: x[0], reverse=True)
        best_score, best_link = scored_links[0]

        reason = (
            f"Matched {best_score} keywords in URL path"
            if best_score > 0
            else "Exploratory navigation to next available internal link"
        )

        next_step = NavigationStep(
            step_number=len(self.navigation_trail) + 1,
            action="FOLLOW_LINK",
            target_url=best_link,
            reason=reason
        )
        self.visited_urls.add(best_link)
        self.navigation_trail.append(next_step)
        return next_step
