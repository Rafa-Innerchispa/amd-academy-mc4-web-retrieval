from src.agent import WebRetrievalAgent
from src.config import AgentConfig
from src.models.schema import RetrievalRequest


def test_no_seed_fails_closed_when_search_disabled():
    agent = WebRetrievalAgent(AgentConfig(enable_public_search=False))
    response = agent.execute(
        RetrievalRequest(query="What is the price of Widget Pro?")
    )
    assert response.status == "FAIL_CLOSED"
    assert response.failure_reason == "NO_SEED_URL"


def test_search_discovers_seed_when_explicitly_enabled():
    query = "What is the price of Widget Pro?"
    agent = WebRetrievalAgent(
        AgentConfig(
            enable_public_search=True,
            total_budget_seconds=5.0,
        )
    )
    agent.search.register_mock(query, ["https://shop.test/widget"])
    agent.browser.register_mock(
        "https://shop.test/widget",
        """
        <html><body>
          <h1>Widget Pro</h1>
          <p>Widget Pro current price: $349.00 USD.</p>
        </body></html>
        """,
    )

    response = agent.execute(RetrievalRequest(query=query))

    assert response.status == "SUCCESS"
    assert response.answer == "$349.00"
    assert response.provenance is not None
    assert response.provenance.source_url == "https://shop.test/widget"
    assert response.metadata["search_used"] is True


def test_search_fail_closed_when_discovery_returns_nothing():
    query = "What is the price of Missing Product?"
    agent = WebRetrievalAgent(AgentConfig(enable_public_search=True))
    agent.search.register_mock(query, [])

    response = agent.execute(RetrievalRequest(query=query))

    assert response.status == "FAIL_CLOSED"
    assert response.failure_reason == "SEARCH_NO_RESULTS"
