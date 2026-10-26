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


def test_navigation_caps_request_timeout_to_remaining_budget(monkeypatch):
    import time

    from src.browser.navigation_engine import NavigationEngine

    class Response:
        status_code = 200
        headers = {}
        text = "<html><body>ok</body></html>"

    captured = {}

    def fake_get(url, **kwargs):
        captured["timeout"] = kwargs["timeout"]
        return Response()

    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *args, **kwargs: [(2, 1, 6, "", ("93.184.216.34", 443))],
    )

    engine = NavigationEngine(timeout=15.0)
    snapshot = engine.fetch(
        "https://example.com/",
        deadline_monotonic=time.monotonic() + 0.5,
    )

    assert snapshot.status_code == 200
    assert 0 < captured["timeout"] <= 0.5


def test_expired_network_deadline_does_not_touch_network(monkeypatch):
    import time

    from src.browser.navigation_engine import NavigationEngine

    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        raise AssertionError("network should not be called after deadline")

    monkeypatch.setattr("requests.get", fake_get)

    engine = NavigationEngine(timeout=15.0)
    snapshot = engine.fetch(
        "https://example.com/",
        deadline_monotonic=time.monotonic() - 1.0,
    )

    assert snapshot.status_code == 504
    assert "TIME_BUDGET_EXCEEDED" in snapshot.raw_html
    assert calls == []


def test_redirect_chain_shares_one_absolute_deadline(monkeypatch):
    from src.browser.navigation_engine import NavigationEngine

    class Redirect:
        status_code = 302
        headers = {"Location": "/final"}
        text = "redirect"

    class Final:
        status_code = 200
        headers = {}
        text = "<html><body>done</body></html>"

    responses = iter([Redirect(), Final()])
    observed_timeouts = []

    def fake_get(url, **kwargs):
        observed_timeouts.append(kwargs["timeout"])
        return next(responses)

    ticks = iter([100.0, 101.0])
    monkeypatch.setattr("src.browser.navigation_engine.time.monotonic", lambda: next(ticks))
    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *args, **kwargs: [(2, 1, 6, "", ("93.184.216.34", 443))],
    )

    engine = NavigationEngine(timeout=15.0)
    snapshot = engine.fetch(
        "https://example.com/start",
        allowed_host="example.com",
        deadline_monotonic=102.0,
    )

    assert snapshot.status_code == 200
    assert observed_timeouts == [2.0, 1.0]
