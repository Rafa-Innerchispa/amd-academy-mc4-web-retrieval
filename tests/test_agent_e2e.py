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
