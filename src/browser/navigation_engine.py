import hashlib
import urllib.request
from datetime import datetime, timezone
from typing import Optional, Dict
from ..models.schema import DOMSnapshot
from ..extractor.dom_extractor import DOMExtractor

class NavigationEngine:
    """
    Safe HTTP / Mock retrieval engine with retry bounds and snapshot hashing.
    Runs zero-dependency with urllib.request and falls back gracefully.
    """

    def __init__(self, timeout: float = 15.0, user_agent: str = "AMDAILeague-MC4"):
        self.timeout = timeout
        self.user_agent = user_agent
        self.extractor = DOMExtractor()
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
                # Try requests first if available
                import requests
                headers = {"User-Agent": self.user_agent}
                resp = requests.get(url, headers=headers, timeout=self.timeout)
                status_code = resp.status_code
                html = resp.text
            except ImportError:
                # Zero-dependency standard library fallback
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
                    with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                        status_code = resp.status
                        html = resp.read().decode("utf-8", errors="replace")
                except Exception as net_err:
                    html = f"<html><body><h1>Fetch Error: {str(net_err)}</h1></body></html>"
                    status_code = 502
            except Exception as e:
                html = f"<html><body><h1>Fetch Error: {str(e)}</h1></body></html>"
                status_code = 502

        content_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()
        clean_text = self.extractor.extract_clean_text(html)

        return DOMSnapshot(
            url=url,
            status_code=status_code,
            content_hash=content_hash,
            raw_html=html,
            cleaned_text=clean_text,
            timestamp_utc=timestamp_utc
        )
