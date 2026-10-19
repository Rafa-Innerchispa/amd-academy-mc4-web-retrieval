from src.agent import WebRetrievalAgent
from src.config import AgentConfig
from src.models.schema import RetrievalRequest


def test_zero_budget_fails_closed_before_fetch():
    agent = WebRetrievalAgent(AgentConfig(total_budget_seconds=0.0))
    agent.browser.register_mock(
        "https://example.test",
        "<html><body><p>Price $10.00</p></body></html>",
    )
    response = agent.execute(
        RetrievalRequest(
            query="What is the price?",
            seed_url="https://example.test",
        )
    )
    assert response.status == "FAIL_CLOSED"
    assert response.failure_reason == "TIME_BUDGET_EXCEEDED"
