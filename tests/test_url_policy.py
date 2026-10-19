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


def test_url_policy_accepts_public_https_domain():
    assert URLPolicy().validate("https://example.com/path") == "https://example.com/path"
