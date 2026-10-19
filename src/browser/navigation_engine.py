import hashlib
import urllib.request
from datetime import datetime, timezone
from typing import Dict

from ..extractor.dom_extractor import DOMExtractor
from ..models.schema import DOMSnapshot
from .url_policy import URLPolicy, URLPolicyError


class NavigationEngine:
    """Bounded HTTP retrieval with provenance snapshots and SSRF protection."""

    def __init__(self, timeout: float = 15.0, user_agent: str = "AMDAILeague-MC4"):
        self.timeout = timeout
        self.user_agent = user_agent
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
                self.url_policy.validate(url)
                try:
                    import requests

                    headers = {"User-Agent": self.user_agent}
                    resp = requests.get(
                        url,
                        headers=headers,
                        timeout=self.timeout,
                        allow_redirects=True,
                    )
                    # Re-check final redirect target to avoid redirect-based SSRF.
                    self.url_policy.validate(resp.url)
                    status_code = resp.status_code
                    html = resp.text
                    url = resp.url
                except ImportError:
                    req = urllib.request.Request(
                        url,
                        headers={"User-Agent": self.user_agent},
                    )
                    with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                        final_url = resp.geturl()
                        self.url_policy.validate(final_url)
                        status_code = resp.status
                        html = resp.read().decode("utf-8", errors="replace")
                        url = final_url
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
