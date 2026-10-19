import re
from typing import Optional
from ..models.schema import ParsedIntent

class IntentParser:
    """
    Deterministic Natural Language Intent Parser.
    Extracts target entities, expected attributes, keywords, and seed URLs.
    """

    URL_REGEX = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]')

    def parse(self, query: str, explicit_seed_url: Optional[str] = None) -> ParsedIntent:
        cleaned_query = query.strip()
        
        # Check for embedded URL
        found_urls = self.URL_REGEX.findall(cleaned_query)
        inferred_seed = explicit_seed_url
        if not inferred_seed and found_urls:
            raw_url = found_urls[0]
            # Strip trailing punctuation commonly appended in natural language sentences
            inferred_seed = raw_url.rstrip("?.,;:!)'\"")

        # Extract words using regex
        words = re.findall(r'[A-Za-z0-9_\-\.]+', cleaned_query)
        stop_words = {
            "what", "is", "the", "of", "and", "in", "on", "for", "a", "an", "at",
            "to", "how", "when", "where", "our", "all", "out", "by", "from", "with",
            "find", "specs", "specs"
        }
        keywords = [
            w.lower().rstrip(".") for w in words
            if w.lower() not in stop_words and len(w) > 2
        ]

        # Extract target attribute heuristics (e.g. date, version, price, count)
        target_attr = "general_information"
        lower_q = cleaned_query.lower()
        if any(k in lower_q for k in ["date", "release", "when", "born", "launched"]):
            target_attr = "date_or_time"
        elif any(k in lower_q for k in ["version", "v1.", "v2.", "v6."]):
            target_attr = "version"
        elif any(k in lower_q for k in ["price", "cost", "fee", "usd", "$"]):
            target_attr = "price"
        elif any(k in lower_q for k in ["who", "founder", "author", "creator", "ceo"]):
            target_attr = "person"
        elif any(k in lower_q for k in ["specification", "specs", "ram", "memory", "tflops"]):
            target_attr = "technical_spec"

        # Prefer a likely entity token over attribute/control words.
        attribute_words = {
            "price", "cost", "fee", "usd", "version", "release", "date",
            "current", "latest", "phone", "telephone", "email", "hours",
            "opening", "closing", "specification", "technical", "memory",
            "ram", "author", "founder", "creator", "ceo",
        }
        entity_candidates = [kw for kw in keywords if kw not in attribute_words]
        target_entity = (
            entity_candidates[0]
            if entity_candidates
            else (keywords[0] if keywords else "unknown_entity")
        )

        return ParsedIntent(
            raw_query=cleaned_query,
            target_entity=target_entity,
            target_attribute=target_attr,
            inferred_seed_url=inferred_seed,
            keywords=keywords
        )
