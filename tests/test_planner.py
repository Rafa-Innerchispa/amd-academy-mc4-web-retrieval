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


def test_planner_normalizes_same_hostname_case_trailing_dot_and_port():
    planner = NavigationPlanner(max_hops=3, lock_domain=True)
    intent = IntentParser().parse(
        "Find product specifications",
        explicit_seed_url="https://Example.COM/start",
    )
    planner.get_initial_step("https://Example.COM/start")
    links = [
        ("https://example.com.:443/specs", "Product specifications"),
        ("https://evil.example.net/specs", "Product specifications"),
    ]
    step = planner.select_next_step("https://Example.COM/start", links, intent)
    assert step is not None
    assert step.target_url == "https://example.com.:443/specs"


def test_planner_backtracks_to_earlier_alternative_after_dead_end():
    planner = NavigationPlanner(max_hops=4, lock_domain=True)
    intent = IntentParser().parse(
        "Find Widget Pro price",
        explicit_seed_url="https://example.com/start",
    )
    planner.get_initial_step("https://example.com/start")

    first = planner.select_next_step(
        "https://example.com/start",
        [
            ("/widget-pro-news", "Widget Pro price announcement"),
            ("/widget-pro-spec", "Widget Pro product price"),
        ],
        intent,
    )
    assert first is not None
    assert first.target_url == "https://example.com/widget-pro-news"

    # The first page is a dead end. The planner should retain and visit the
    # second-best link discovered on the seed page instead of stopping.
    second = planner.select_next_step(first.target_url, [], intent)
    assert second is not None
    assert second.target_url == "https://example.com/widget-pro-spec"


def test_planner_frontier_stays_bounded():
    planner = NavigationPlanner(max_hops=3, lock_domain=True, max_frontier=5)
    intent = IntentParser().parse(
        "Find specifications",
        explicit_seed_url="https://example.com/start",
    )
    planner.get_initial_step("https://example.com/start")
    links = [(f"/item/{i}", f"item {i}") for i in range(30)]
    planner._add_to_frontier("https://example.com/start", links, intent)
    assert len(planner._frontier) == 5
