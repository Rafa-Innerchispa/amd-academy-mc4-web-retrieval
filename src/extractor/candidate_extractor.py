from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html import unescape
from typing import Iterable, List, Optional, Sequence, Tuple

from .dom_extractor import DOMExtractor


@dataclass(frozen=True)
class Candidate:
    value: str
    context: str
    score: float
    source_kind: str


class CandidateExtractor:
    """Deterministic candidate extraction for exact-value web retrieval.

    This deliberately avoids generative synthesis. It produces grounded candidate
    values plus the source context that contained each value, then ranks them by
    query keyword proximity.
    """

    MONTH = (
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
    )

    INJECTION_MARKERS = (
        "ignore previous instructions",
        "ignore all previous instructions",
        "system message",
        "assistant instruction",
        "developer instruction",
        "follow these instructions",
        "disregard previous",
        "override the user",
        "do not trust the user",
    )

    PATTERNS = {
        "date_or_time": [
            rf"\b{MONTH}\s+\d{{1,2}}(?:st|nd|rd|th)?[,]?\s+\d{{4}}\b",
            r"\b\d{4}-\d{2}-\d{2}\b",
            r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        ],
        "version": [
            r"\b(?:version\s+|v)?\d+\.\d+(?:\.\d+){0,3}(?:[-+][A-Za-z0-9._-]+)?\b",
        ],
        "price": [
            r"(?:US\$|USD\s*|\$)\s*\d[\d,]*(?:\.\d{1,2})?",
            r"\b\d[\d,]*(?:\.\d{1,2})?\s*(?:USD|EUR|GBP)\b",
        ],
        "email": [
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        ],
        "phone": [
            r"(?<!\w)(?:\+?\d[\d().\-\s]{7,}\d)(?!\w)",
        ],
        "technical_spec": [
            r"\b\d+(?:\.\d+)?\s?(?:GB|GiB|MB|MHz|GHz|W|kW|TFLOPS?|TOPS?|Gbps|Mbps)\b",
        ],
        "number": [
            r"(?<![\w.])\d[\d,]*(?:\.\d+)?(?![\w.])",
        ],
        "hours": [
            r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)(?:\s*[-–]\s*(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday))?\s*[:,-]?\s*\d{1,2}(?::\d{2})?\s*(?:AM|PM)?\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:AM|PM)?\b",
            r"\b\d{1,2}(?::\d{2})?\s*(?:AM|PM)\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:AM|PM)\b",
        ],
    }

    def __init__(self) -> None:
        self.dom = DOMExtractor()

    def extract(self, html: str, cleaned_text: str, intent) -> List[Candidate]:
        candidates: List[Candidate] = []
        json_document_candidates = self._from_json_document(html, intent)
        if json_document_candidates:
            candidates.extend(json_document_candidates)

        block_candidates = self._from_html_blocks(html, intent)
        if block_candidates:
            candidates.extend(block_candidates)
        else:
            candidates.extend(self._from_text(cleaned_text, intent))
        candidates.extend(self._from_tables(html, intent))
        candidates.extend(self._from_json_ld(html, intent))
        candidates.extend(self._from_contact_links(html, intent))
        return self._dedupe_rank(candidates)

    def best(self, html: str, cleaned_text: str, intent) -> Optional[Candidate]:
        ranked = self.extract(html, cleaned_text, intent)
        return ranked[0] if ranked else None

    def _from_text(self, text: str, intent) -> List[Candidate]:
        attr = self._effective_attribute(intent)
        patterns = self.PATTERNS.get(attr, [])
        if attr == "person":
            return self._person_candidates(text, intent)
        if not patterns and attr == "general_information":
            return self._general_sentences(text, intent)

        found: List[Candidate] = []
        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                value = self._normalize_value(match.group(0).strip(), attr)
                guard_context = text[
                    max(0, match.start() - 240): min(len(text), match.end() + 240)
                ]
                if self._looks_like_untrusted_instruction(guard_context):
                    continue
                context = self._context(text, match.start(), match.end())
                found.append(
                    Candidate(
                        value=value,
                        context=context,
                        score=self._score_context(context, intent),
                        source_kind="text",
                    )
                )
        return found

    def _from_html_blocks(self, html: str, intent) -> List[Candidate]:
        """Extract candidates within semantic HTML blocks to avoid cross-block leakage."""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            blocks = []
            for node in soup.find_all(
                ["p", "li", "dd", "dt", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th"]
            ):
                text = re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()
                if text:
                    blocks.append(text)
        except ImportError:
            blocks = [
                re.sub(r"<[^>]+>", " ", match.group(1)).strip()
                for match in re.finditer(
                    r"<(?:p|li|dd|dt|h[1-6]|td|th)\b[^>]*>(.*?)</(?:p|li|dd|dt|h[1-6]|td|th)>",
                    html,
                    flags=re.IGNORECASE | re.DOTALL,
                )
            ]

        out: List[Candidate] = []
        for block in blocks:
            out.extend(self._from_text(block, intent))
        return out

    def _from_tables(self, html: str, intent) -> List[Candidate]:
        out: List[Candidate] = []
        for table in self.dom.extract_tables(html):
            for row in table:
                row_text = " | ".join(f"{k}: {v}" for k, v in row.items())
                if self._looks_like_untrusted_instruction(row_text):
                    continue
                score = self._score_context(row_text, intent) + 1.5
                for value in row.values():
                    for candidate in self._extract_values_from_fragment(str(value), intent):
                        out.append(
                            Candidate(
                                value=candidate,
                                context=row_text,
                                score=score,
                                source_kind="table",
                            )
                        )
        return out

    def _from_contact_links(self, html: str, intent) -> List[Candidate]:
        attr = self._effective_attribute(intent)
        if attr not in {"email", "phone"}:
            return []
        values = self.dom.extract_contact_values(html).get(attr, [])
        out: List[Candidate] = []
        for value in values:
            normalized = self._normalize_value(value, attr)
            context = f"{attr}: {normalized}"
            out.append(
                Candidate(
                    value=normalized,
                    context=context,
                    score=self._score_context(context, intent) + 2.5,
                    source_kind=f"{attr}_link",
                )
            )
        return out

    def _from_json_document(self, raw: str, intent) -> List[Candidate]:
        """Extract grounded values from a response whose body is JSON.

        Match 4 may encounter API endpoints rather than rendered HTML. Keep
        sibling scalar fields together so entity names, units and values can
        contribute to relevance scoring without requiring an LLM.
        """
        stripped = raw.strip()
        if not stripped or stripped[0] not in "[{":
            return []
        try:
            parsed = json.loads(stripped)
        except Exception:
            return []

        attr = self._effective_attribute(intent)
        path_terms = {
            "price": ("price", "cost", "amount", "fee"),
            "date_or_time": ("date", "release", "released", "published", "created", "updated"),
            "version": ("version", "release", "revision"),
            "email": ("email", "mail"),
            "phone": ("phone", "telephone", "tel"),
            "hours": ("hours", "opening", "closing", "schedule"),
            "number": ("count", "total", "number", "quantity"),
            "person": ("author", "founder", "creator", "ceo", "name"),
            "technical_spec": (
                "memory", "ram", "capacity", "speed", "power",
                "tflops", "tops", "bandwidth",
            ),
        }.get(attr, ())

        out: List[Candidate] = []
        for path, value, record_context in self._walk_json_records(parsed):
            fragment = str(value)
            path_text = " ".join(path)
            context = f"{path_text}: {fragment} | {record_context}".strip(" |")
            if self._looks_like_untrusted_instruction(context):
                continue

            values = self._extract_values_from_fragment(fragment, intent)
            path_lower = path_text.lower()
            if not values and path_terms and any(term in path_lower for term in path_terms):
                normalized = self._normalize_value(fragment, attr)
                if normalized:
                    values = [normalized]

            score = self._score_context(context, intent) + 2.25
            for candidate in values:
                out.append(
                    Candidate(
                        value=candidate,
                        context=context,
                        score=score,
                        source_kind="json_document",
                    )
                )
        return out

    def _walk_json_records(
        self, value, path: Tuple[str, ...] = ()
    ) -> Iterable[Tuple[Tuple[str, ...], object, str]]:
        if isinstance(value, dict):
            scalar_items = [
                (str(key), child)
                for key, child in value.items()
                if isinstance(child, (str, int, float, bool)) and child is not None
            ]
            record_context = " | ".join(
                f"{key}: {child}" for key, child in scalar_items
            )
            for key, child in scalar_items:
                yield path + (key,), child, record_context
            for key, child in value.items():
                if isinstance(child, (dict, list)):
                    yield from self._walk_json_records(child, path + (str(key),))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from self._walk_json_records(child, path + (str(index),))

    def _from_json_ld(self, html: str, intent) -> List[Candidate]:
        out: List[Candidate] = []
        blocks = re.findall(
            r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        for raw in blocks:
            try:
                parsed = json.loads(unescape(raw).strip())
            except Exception:
                continue
            for path, value in self._walk_json(parsed):
                if not isinstance(value, (str, int, float)):
                    continue
                fragment = str(value)
                path_text = " ".join(path)
                context = f"{path_text}: {fragment}".strip()
                if self._looks_like_untrusted_instruction(context):
                    continue
                score = self._score_context(context, intent) + 2.0
                for candidate in self._extract_values_from_fragment(fragment, intent):
                    out.append(
                        Candidate(
                            value=candidate,
                            context=context,
                            score=score,
                            source_kind="json_ld",
                        )
                    )
        return out

    def _walk_json(self, value, path: Tuple[str, ...] = ()) -> Iterable[Tuple[Tuple[str, ...], object]]:
        if isinstance(value, dict):
            for key, child in value.items():
                yield from self._walk_json(child, path + (str(key),))
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                yield from self._walk_json(child, path + (str(idx),))
        else:
            yield path, value

    def _person_candidates(self, text: str, intent) -> List[Candidate]:
        labels = r"(?:CEO|chief executive officer|founder|co-founder|author|creator|director|president)"
        pattern = re.compile(
            labels
            + r"\s*(?:is|:|-)?\s*"
            + r"([A-Z][A-Za-z.'’-]+(?:\s+[A-Z][A-Za-z.'’-]+){1,3})",
            re.IGNORECASE,
        )
        out: List[Candidate] = []
        for match in pattern.finditer(text):
            value = self._normalize_value(match.group(1).strip(), "person")
            guard_context = text[
                max(0, match.start() - 240): min(len(text), match.end() + 240)
            ]
            if self._looks_like_untrusted_instruction(guard_context):
                continue
            context = self._context(text, match.start(), match.end())
            out.append(
                Candidate(
                    value=value,
                    context=context,
                    score=self._score_context(context, intent) + 1.0,
                    source_kind="text",
                )
            )
        return out

    def _normalize_value(self, value: str, attr: str) -> str:
        value = re.sub(r"\s+", " ", value).strip()
        if attr == "version":
            value = re.sub(r"^(?:version\s+|v(?=\d))", "", value, flags=re.IGNORECASE)
        if attr in {"phone", "email", "person"}:
            value = value.strip(" .,;:")
        return value

    def _general_sentences(self, text: str, intent) -> List[Candidate]:
        parts = re.split(r"(?<=[.!?])\s+", text)
        out: List[Candidate] = []
        for sentence in parts:
            if self._looks_like_untrusted_instruction(sentence):
                continue
            score = self._score_context(sentence, intent)
            if score > 0 and 2 <= len(sentence.split()) <= 45:
                out.append(
                    Candidate(
                        value=sentence.strip(),
                        context=sentence.strip(),
                        score=score,
                        source_kind="sentence",
                    )
                )
        return out

    def _effective_attribute(self, intent) -> str:
        q = intent.raw_query.lower()
        if "email" in q or "e-mail" in q:
            return "email"
        if "phone" in q or "telephone" in q or "call" in q:
            return "phone"
        if "hours" in q or "open" in q or "closing" in q:
            return "hours"
        if "how many" in q or "number of" in q or "count of" in q:
            return "number"
        return intent.target_attribute

    def _extract_values_from_fragment(self, fragment: str, intent) -> List[str]:
        attr = self._effective_attribute(intent)
        patterns = self.PATTERNS.get(attr, [])
        values: List[str] = []
        for pattern in patterns:
            values.extend(
                self._normalize_value(m.group(0).strip(), attr)
                for m in re.finditer(pattern, fragment, flags=re.IGNORECASE)
            )
        if not values and attr == "general_information" and fragment.strip():
            values.append(fragment.strip())
        return values

    def _looks_like_untrusted_instruction(self, context: str) -> bool:
        lower = context.lower()
        return any(marker in lower for marker in self.INJECTION_MARKERS)

    def _score_context(self, context: str, intent) -> float:
        lower = context.lower()
        keywords = [k.lower() for k in intent.keywords if len(k) >= 3]
        matched = sum(1 for kw in keywords if self._contains_term(lower, kw))
        entity_bonus = (
            1.5
            if intent.target_entity
            and self._contains_term(lower, intent.target_entity.lower())
            else 0.0
        )
        attr_words = {
            "price": ("price", "cost", "usd", "$"),
            "version": ("version", "release", "firmware"),
            "date_or_time": ("date", "released", "published", "launched"),
            "technical_spec": ("memory", "ram", "spec", "capacity", "speed", "power"),
            "hours": ("hours", "open", "opening", "closing"),
            "number": ("number", "count", "total"),
            "phone": ("phone", "telephone", "call"),
            "email": ("email", "contact"),
            "person": ("author", "founder", "creator", "ceo"),
        }.get(intent.target_attribute, ())
        attr_bonus = 0.75 * sum(1 for word in attr_words if word in lower)
        return matched * 2.0 + entity_bonus + attr_bonus

    def _contains_term(self, text: str, term: str) -> bool:
        """Match query terms as lexical units instead of arbitrary substrings."""
        term = term.strip().lower()
        if not term:
            return False
        return re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])",
            text,
            flags=re.IGNORECASE,
        ) is not None

    def _context(self, text: str, start: int, end: int, radius: int = 180) -> str:
        """Return the sentence containing the candidate when possible.

        Sentence boundaries are punctuation followed by whitespace/end, so
        decimal/version dots such as 6.2 or 10.1.0 are not mistaken for stops.
        """
        boundaries = [0]
        boundaries.extend(
            match.end()
            for match in re.finditer(r"[.!?](?=\s|$)", text)
        )
        if boundaries[-1] != len(text):
            boundaries.append(len(text))

        for left, right in zip(boundaries, boundaries[1:]):
            if left <= start < right:
                sentence = text[left:right].strip()
                if sentence and len(sentence) <= radius * 2:
                    return sentence
                break

        left = max(0, start - radius)
        right = min(len(text), end + radius)
        return text[left:right].strip()

    def _dedupe_rank(self, candidates: Sequence[Candidate]) -> List[Candidate]:
        best_by_value = {}
        for item in candidates:
            key = re.sub(r"\s+", " ", item.value.strip().lower())
            if not key:
                continue
            previous = best_by_value.get(key)
            if previous is None or item.score > previous.score:
                best_by_value[key] = item
        return sorted(
            best_by_value.values(),
            key=lambda item: (item.score, len(item.context)),
            reverse=True,
        )
