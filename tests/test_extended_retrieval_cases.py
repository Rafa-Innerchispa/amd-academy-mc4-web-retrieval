from src.extractor.candidate_extractor import CandidateExtractor
from src.parser.intent_parser import IntentParser


def test_opening_hours_extraction():
    text = "Chispa Lab opening hours: Monday-Friday 9:00 AM - 5:00 PM."
    intent = IntentParser().parse(
        "What are the opening hours for Chispa Lab?",
        explicit_seed_url="https://example.com",
    )
    best = CandidateExtractor().best("<html></html>", text, intent)
    assert best is not None
    assert best.value == "Monday-Friday 9:00 AM - 5:00 PM"


def test_version_is_normalized_to_value_only():
    intent = IntentParser().parse(
        "What is the current ROCm version?",
        explicit_seed_url="https://example.com",
    )
    best = CandidateExtractor().best(
        "<html></html>",
        "Current ROCm release version 10.1.0 is recommended.",
        intent,
    )
    assert best is not None
    assert best.value == "10.1.0"


def test_person_label_extraction():
    intent = IntentParser().parse(
        "Who is the CEO of AMD?",
        explicit_seed_url="https://example.com",
    )
    best = CandidateExtractor().best(
        "<html></html>",
        "AMD CEO: Lisa Su.",
        intent,
    )
    assert best is not None
    assert best.value == "Lisa Su"


def test_mailto_contact_extraction():
    html = '<a href="mailto:support@chispa.example">Support</a>'
    intent = IntentParser().parse(
        "What is the email for Chispa Support?",
        explicit_seed_url="https://example.com",
    )
    best = CandidateExtractor().best(html, "Support", intent)
    assert best is not None
    assert best.value == "support@chispa.example"
