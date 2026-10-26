from src.agent import WebRetrievalAgent
from src.config import AgentConfig
from src.models.schema import RetrievalRequest


class RecordingReranker:
    def __init__(self):
        self.calls = 0

    def rerank(self, *, query, candidates, page_text):
        self.calls += 1
        return list(reversed(candidates))


def test_reranker_is_not_called_when_top_candidate_is_clear():
    reranker = RecordingReranker()
    agent = WebRetrievalAgent(reranker=reranker)
    agent.browser.register_mock(
        "https://gate.test/clear",
        "<html><body><p>Widget Pro current price: $349.00 USD.</p></body></html>",
    )

    response = agent.execute(RetrievalRequest(
        query="What is the current price of Widget Pro?",
        seed_url="https://gate.test/clear",
    ))

    assert response.status == "SUCCESS"
    assert reranker.calls == 0
    assert response.metadata["ambiguity_detected"] is False
    assert response.metadata["reranker_used"] is False
    assert response.answer in {"$349.00", "349.00 USD"}


def test_reranker_is_called_only_for_close_competing_candidates():
    reranker = RecordingReranker()
    config = AgentConfig(reranker_margin_threshold=10.0)
    agent = WebRetrievalAgent(config=config, reranker=reranker)
    agent.browser.register_mock(
        "https://gate.test/ambiguous",
        """
        <html><body>
          <p>Widget Pro price option one: $349.00 USD.</p>
          <p>Widget Pro price option two: $359.00 USD.</p>
        </body></html>
        """,
    )

    response = agent.execute(RetrievalRequest(
        query="What is the price of Widget Pro?",
        seed_url="https://gate.test/ambiguous",
    ))

    assert response.status == "SUCCESS"
    assert reranker.calls == 1
    assert response.metadata["ambiguity_detected"] is True
    assert response.metadata["reranker_used"] is True


def test_reranker_cannot_invent_candidates_through_protocol_contract():
    reranker = RecordingReranker()
    config = AgentConfig(reranker_margin_threshold=10.0)
    agent = WebRetrievalAgent(config=config, reranker=reranker)
    agent.browser.register_mock(
        "https://gate.test/grounded",
        """
        <html><body>
          <p>Widget Pro price option one: $349.00 USD.</p>
          <p>Widget Pro price option two: $359.00 USD.</p>
        </body></html>
        """,
    )

    response = agent.execute(RetrievalRequest(
        query="What is the price of Widget Pro?",
        seed_url="https://gate.test/grounded",
    ))

    assert response.answer in {"$349.00", "349.00 USD", "$359.00", "359.00 USD"}
    assert response.provenance is not None
    assert response.provenance.source_url == "https://gate.test/grounded"
