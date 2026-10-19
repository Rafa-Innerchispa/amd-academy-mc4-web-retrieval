import hashlib
from datetime import datetime, timezone
from typing import Dict
from urllib.parse import urljoin

from ..extractor.dom_extractor import DOMExtractor
from ..models.schema import DOMSnapshot
from .url_policy import URLPolicy, URLPolicyError


class NavigationEngine:
    """Bounded HTTP retrieval with provenance snapshots and URL safety checks."""

    REDIRECT_CODES = {301, 302, 303, 307, 308}

    def __init__(
        self,
        timeout: float = 15.0,
        user_agent: str = "AMDAILeague-MC4",
        max_redirects: int = 5,
    ):
        self.timeout = timeout
        self.user_agent = user_agent
        self.max_redirects = max_redirects
        self.extractor = DOMExtractor()
        self.url_policy = URLPolicy()
        self._mock_responses: Dict[str, str] = {}

    def register_mock(self, url: str, html_body: str):
        self._mock_responses[url] = html_body

    def fetch(self, url: str) -> DOMSnapshot:
        timestamp_utc = datetime.now(timezone.utc).isoformat()

        if url in self._mock_responses:
            html = self._mock_responses[url]
            status_code = 200
        else:
            try:
                import requests

                current_url = url
                response = None
                for _ in range(self.max_redirects + 1):
                    self.url_policy.validate(current_url)
                    response = requests.get(
                        current_url,
                        headers={"User-Agent": self.user_agent},
                        timeout=self.timeout,
                        allow_redirects=False,
                    )

                    if response.status_code not in self.REDIRECT_CODES:
                        break

                    location = response.headers.get("Location")
                    if not location:
                        break

                    next_url = urljoin(current_url, location)
                    # Validate BEFORE following so a public URL cannot redirect
                    # the agent into localhost, metadata services, or RFC1918.
                    self.url_policy.validate(next_url)
                    current_url = next_url
                else:
                    raise RuntimeError("TOO_MANY_REDIRECTS")

                if response is None:
                    raise RuntimeError("NO_HTTP_RESPONSE")

                url = current_url
                status_code = response.status_code
                html = response.text

            except URLPolicyError as exc:
                html = f"<html><body>Blocked URL: {exc}</body></html>"
                status_code = 403
            except Exception as exc:
                html = f"<html><body>Fetch Error: {type(exc).__name__}</body></html>"
                status_code = 502

        content_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()
        clean_text = self.extractor.extract_clean_text(html)

        return DOMSnapshot(
            url=url,
            status_code=status_code,
            content_hash=content_hash,
            raw_html=html,
            cleaned_text=clean_text,
            timestamp_utc=timestamp_utc,
        )
