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


def test_lead_time_duration_extraction():
    intent = IntentParser().parse(
        "What is the lead time for Widget Pro?",
        explicit_seed_url="https://example.com/widget",
    )
    best = CandidateExtractor().best(
        "<html></html>",
        "Widget Pro standard lead time is 3-5 business days.",
        intent,
    )
    assert intent.target_attribute == "duration"
    assert best is not None
    assert best.value == "3-5 business days"


def test_temperature_technical_spec_extraction():
    intent = IntentParser().parse(
        "What is the maximum temperature for Module X?",
        explicit_seed_url="https://example.com/module-x",
    )
    best = CandidateExtractor().best(
        "<html></html>",
        "Module X maximum operating temperature is 95 °C.",
        intent,
    )
    assert intent.target_attribute == "technical_spec"
    assert best is not None
    assert best.value == "95 °C"


def test_voltage_and_weight_technical_specs():
    extractor = CandidateExtractor()

    voltage_intent = IntentParser().parse("What is the input voltage of Unit A?")
    voltage = extractor.best(
        "<html></html>",
        "Unit A input voltage: 12 V.",
        voltage_intent,
    )
    assert voltage is not None
    assert voltage.value == "12 V"

    weight_intent = IntentParser().parse("What is the weight of Unit A?")
    weight = extractor.best(
        "<html></html>",
        "Unit A shipping weight: 2.4 kg.",
        weight_intent,
    )
    assert weight is not None
    assert weight.value == "2.4 kg"


def test_latency_and_percentage_exact_values():
    extractor = CandidateExtractor()

    latency_intent = IntentParser().parse("What is the latency of Service X?")
    latency = extractor.best(
        "<html></html>",
        "Service X median latency is 0.8 ms.",
        latency_intent,
    )
    assert latency is not None
    assert latency.value == "0.8 ms"

    percentage_intent = IntentParser().parse("What is the efficiency percentage of Unit A?")
    percentage = extractor.best(
        "<html></html>",
        "Unit A conversion efficiency is 99.9%.",
        percentage_intent,
    )
    assert percentage_intent.target_attribute == "percentage"
    assert percentage is not None
    assert percentage.value == "99.9%"
