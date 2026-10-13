from src.parser.intent_parser import IntentParser

def test_intent_parser_extracts_url_and_keywords():
    parser = IntentParser()
    query = "What is the release date of ROCm 6.2 on https://rocm.docs.amd.com?"
    intent = parser.parse(query)

    assert intent.inferred_seed_url == "https://rocm.docs.amd.com"
    assert intent.target_attribute == "date_or_time"
    assert "rocm" in intent.keywords

def test_intent_parser_with_explicit_seed():
    parser = IntentParser()
    query = "Find the latest hardware specs for Instinct MI300X"
    intent = parser.parse(query, explicit_seed_url="https://www.amd.com/en/products/accelerators/instinct.html")

    assert intent.inferred_seed_url == "https://www.amd.com/en/products/accelerators/instinct.html"
    assert intent.target_attribute == "technical_spec"
    assert "instinct" in intent.keywords
