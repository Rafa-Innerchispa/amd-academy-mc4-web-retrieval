from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import parse_qs, unquote, urlparse


@dataclass(frozen=True)
class SearchResult:
    url: str
    title: str = ""
    snippet: str = ""
    score: float = 0.0


class SearchEngine:
    """Optional keyless public-web discovery.

    Search is deliberately separate from the graded retrieval core. It is
    disabled by default and can be enabled for the product/demo path when no
    starting URL is supplied.
    """

    def __init__(
        self,
        *,
        endpoint: str = "https://html.duckduckgo.com/html/",
        timeout_seconds: float = 8.0,
        max_results: int = 5,
    ):
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self.max_results = max_results
        self._mocks: Dict[str, List[SearchResult]] = {}

    def register_mock(self, query: str, urls: List[str]) -> None:
        self._mocks[query.strip()] = [
            SearchResult(url=url, title=url, score=float(len(urls) - index))
            for index, url in enumerate(urls)
        ]

    def search(self, query: str) -> List[SearchResult]:
        normalized = query.strip()
        if not normalized:
            return []
        if normalized in self._mocks:
            return self._mocks[normalized][: self.max_results]

        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(
                self.endpoint,
                params={"q": normalized},
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; InnerOSMatch4/0.2; "
                        "+https://github.com/Rafa-Innerchispa)"
                    )
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            results: List[SearchResult] = []
            seen = set()

            for anchor in soup.select("a.result__a, .result a[href]"):
                href = str(anchor.get("href") or "").strip()
                url = self._decode_result_url(href)
                if not url or url in seen:
                    continue
                parsed = urlparse(url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    continue
                seen.add(url)

                title = anchor.get_text(" ", strip=True)
                container = anchor.find_parent(class_="result")
                snippet = ""
                if container is not None:
                    snippet_el = container.select_one(".result__snippet")
                    if snippet_el is not None:
                        snippet = snippet_el.get_text(" ", strip=True)

                results.append(
                    SearchResult(
                        url=url,
                        title=title,
                        snippet=snippet,
                        score=self._score(normalized, title, snippet, url),
                    )
                )
                if len(results) >= self.max_results:
                    break

            return sorted(results, key=lambda item: item.score, reverse=True)
        except Exception:
            return []

    def _decode_result_url(self, href: str) -> str:
        if not href:
            return ""
        if href.startswith("//"):
            href = "https:" + href
        parsed = urlparse(href)
        if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
            params = parse_qs(parsed.query)
            target = (params.get("uddg") or [""])[0]
            return unquote(target)
        return href

    def _score(self, query: str, title: str, snippet: str, url: str) -> float:
        terms = [
            token.lower()
            for token in query.replace("/", " ").replace("-", " ").split()
            if len(token) >= 3
        ]
        title_l = title.lower()
        snippet_l = snippet.lower()
        url_l = url.lower()
        return (
            sum(3.0 for term in terms if term in title_l)
            + sum(1.5 for term in terms if term in snippet_l)
            + sum(1.0 for term in terms if term in url_l)
        )
