from src.planner.navigation_planner import NavigationPlanner
from src.parser.intent_parser import IntentParser

def test_planner_bounds_and_loop_prevention():
    planner = NavigationPlanner(max_hops=3, lock_domain=True)
    parser = IntentParser()
    intent = parser.parse("Find benchmark numbers for ROCm", explicit_seed_url="https://example.com/start")

    # Initial step
    step1 = planner.get_initial_step("https://example.com/start")
    assert step1.step_number == 1
    assert step1.action == "VISIT_URL"

    # Select next step
    links = [
        "https://example.com/start", # loop, should be skipped
        "https://malicious.com/phish", # foreign domain, should be skipped
        "https://example.com/benchmarks", # matches kw "benchmark"
    ]
    step2 = planner.select_next_step("https://example.com/start", links, intent)
    assert step2 is not None
    assert step2.target_url == "https://example.com/benchmarks"

    # Third step
    links_step3 = ["https://example.com/results"]
    step3 = planner.select_next_step(step2.target_url, links_step3, intent)
    assert step3 is not None
    assert step3.step_number == 3

    # Fourth step should exceed max_hops (3) and return None
    links_step4 = ["https://example.com/end"]
    step4 = planner.select_next_step(step3.target_url, links_step4, intent)
    assert step4 is None


def test_planner_uses_anchor_text_when_url_is_opaque():
    planner = NavigationPlanner(max_hops=3, lock_domain=True)
    intent = IntentParser().parse(
        "Find the R9700 specifications",
        explicit_seed_url="https://example.com/start",
    )
    planner.get_initial_step("https://example.com/start")
    links = [
        ("/p/123", "General accessories"),
        ("/p/999", "R9700 specifications and memory"),
    ]
    step = planner.select_next_step("https://example.com/start", links, intent)
    assert step is not None
    assert step.target_url == "https://example.com/p/999"
