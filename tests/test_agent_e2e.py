from src.agent import WebRetrievalAgent
from src.models.schema import RetrievalRequest, VerificationStatus

def test_agent_end_to_end_verified_retrieval():
    agent = WebRetrievalAgent()

    # Register mock pages
    seed_html = """
    <html>
        <body>
            <h1>Welcome to ROCm Hub</h1>
            <p>Looking for details? Visit our <a href="https://rocm.hub/releases">Releases Page</a>.</p>
        </body>
    </html>
    """
    releases_html = """
    <html>
        <body>
            <h1>ROCm Release Information</h1>
            <p>ROCm 6.2 was officially published on July 22, 2024.</p>
        </body>
    </html>
    """
    agent.browser.register_mock("https://rocm.hub/start", seed_html)
    agent.browser.register_mock("https://rocm.hub/releases", releases_html)

    req = RetrievalRequest(
        query="What is the release date of ROCm 6.2?",
        seed_url="https://rocm.hub/start",
        max_hops=3
    )

    resp = agent.execute(req)

    assert resp.status == "SUCCESS"
    assert resp.verification_status == VerificationStatus.VERIFIED
    assert resp.answer == "July 22, 2024"
    assert resp.provenance is not None
    assert resp.provenance.source_url == "https://rocm.hub/releases"
    assert len(resp.navigation_trail) == 2

def test_agent_fails_closed_when_info_not_found():
    agent = WebRetrievalAgent()
    empty_html = """
    <html>
        <body>
            <h1>Documentation</h1>
            <p>Nothing relevant here.</p>
        </body>
    </html>
    """
    agent.browser.register_mock("https://empty.test/page", empty_html)

    req = RetrievalRequest(
        query="When was the project launched?",
        seed_url="https://empty.test/page",
        max_hops=2
    )

    resp = agent.execute(req)

    assert resp.status == "FAIL_CLOSED"
    assert resp.verification_status == VerificationStatus.REJECTED_UNVERIFIED
    assert resp.failure_reason == "CLAIM_NOT_FOUND_OR_UNVERIFIED_IN_EVIDENCE"


def test_agent_skips_unrelated_price_and_follows_relevant_link():
    agent = WebRetrievalAgent()
    agent.browser.register_mock(
        "https://shop.test/start",
        """
        <html><body>
          <p>Standard shipping costs $19.99.</p>
          <a href="/p/999">R9700 workstation details and price</a>
        </body></html>
        """,
    )
    agent.browser.register_mock(
        "https://shop.test/p/999",
        """
        <html><body>
          <h1>R9700 workstation</h1>
          <p>R9700 workstation current price: $1299.00 USD.</p>
        </body></html>
        """,
    )
    resp = agent.execute(
        RetrievalRequest(
            query="What is the price of the R9700 workstation?",
            seed_url="https://shop.test/start",
            max_hops=3,
        )
    )
    assert resp.status == "SUCCESS"
    assert resp.answer == "$1299.00"
    assert resp.provenance is not None
    assert resp.provenance.source_url == "https://shop.test/p/999"



def test_agent_follows_pagination_to_requested_value():
    agent = WebRetrievalAgent()
    agent.browser.register_mock(
        "https://shop.test/catalog?page=1",
        """
        <html><body>
          <h1>Catalog</h1>
          <a href="/help">Help</a>
          <a href="/catalog?page=2">Next</a>
        </body></html>
        """,
    )
    agent.browser.register_mock(
        "https://shop.test/catalog?page=2",
        """
        <html><body>
          <p>Widget Pro current price: $349.00 USD.</p>
        </body></html>
        """,
    )
    response = agent.execute(
        RetrievalRequest(
            query="What is the price of Widget Pro?",
            seed_url="https://shop.test/catalog?page=1",
            max_hops=3,
        )
    )

    assert response.status == "SUCCESS"
    assert response.answer == "$349.00"
    assert response.provenance is not None
    assert response.provenance.source_url == "https://shop.test/catalog?page=2"
    assert len(response.navigation_trail) == 2


def test_agent_backtracks_from_relevant_decoy_to_second_candidate():
    agent = WebRetrievalAgent()
    agent.browser.register_mock(
        "https://shop.test/start",
        """
        <html><body>
          <a href="/news">Widget Pro price current official announcement</a>
          <a href="/product">Widget Pro details</a>
        </body></html>
        """,
    )
    agent.browser.register_mock(
        "https://shop.test/news",
        "<html><body><p>Announcement only. No price listed.</p></body></html>",
    )
    agent.browser.register_mock(
        "https://shop.test/product",
        "<html><body><p>Widget Pro current price: $349.00 USD.</p></body></html>",
    )

    response = agent.execute(
        RetrievalRequest(
            query="What is the price of Widget Pro?",
            seed_url="https://shop.test/start",
            max_hops=4,
        )
    )

    assert response.status == "SUCCESS"
    assert response.answer == "$349.00"
    assert response.provenance is not None
    assert response.provenance.source_url == "https://shop.test/product"
    assert [step.target_url for step in response.navigation_trail] == [
        "https://shop.test/start",
        "https://shop.test/news",
        "https://shop.test/product",
    ]
