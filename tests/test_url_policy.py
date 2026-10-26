import pytest

from src.browser.url_policy import URLPolicy, URLPolicyError


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/admin",
        "http://localhost:8000/",
        "http://10.0.0.5/",
        "http://192.168.1.10/",
        "http://169.254.169.254/latest/meta-data/",
        "file:///etc/passwd",
    ],
)
def test_url_policy_blocks_private_and_non_http_targets(url):
    with pytest.raises(URLPolicyError):
        URLPolicy().validate(url)


def test_url_policy_accepts_public_https_domain(monkeypatch):
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda *args, **kwargs: [(2, 1, 6, "", ("93.184.216.34", 443))],
    )
    assert URLPolicy().validate("https://example.com/path") == "https://example.com/path"


def test_navigation_blocks_redirect_to_private_ip(monkeypatch):
    from src.browser.navigation_engine import NavigationEngine

    class Response:
        status_code = 302
        headers = {"Location": "http://127.0.0.1/admin"}
        text = "redirect"

    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return Response()

    monkeypatch.setattr("requests.get", fake_get)
    snapshot = NavigationEngine().fetch("https://public.invalid/start")

    assert snapshot.status_code == 403
    assert calls == ["https://public.invalid/start"]


def test_url_policy_can_allow_explicit_internal_grader_host():
    policy = URLPolicy(allowed_private_hosts=["127.0.0.1"])
    assert (
        policy.validate("http://127.0.0.1:8080/task")
        == "http://127.0.0.1:8080/task"
    )


def test_navigation_blocks_redirect_to_different_public_domain(monkeypatch):
    from src.browser.navigation_engine import NavigationEngine

    class Response:
        status_code = 302
        headers = {"Location": "https://other.example.net/landing"}
        text = "redirect"

    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return Response()

    monkeypatch.setattr("requests.get", fake_get)
    monkeypatch.setattr(
        "socket.getaddrinfo",
        lambda host, *args, **kwargs: [(2, 1, 6, "", ("93.184.216.34", 443))],
    )

    snapshot = NavigationEngine().fetch(
        "https://example.com/start",
        allowed_host="example.com",
    )

    assert snapshot.status_code == 403
    assert calls == ["https://example.com/start"]
    assert "CROSS_DOMAIN_REDIRECT_BLOCKED" in snapshot.raw_html
