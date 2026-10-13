from src.verifier.fail_closed_verifier import FailClosedVerifier
from src.models.schema import DOMSnapshot, VerificationStatus

def test_verifier_accepts_grounded_answer():
    verifier = FailClosedVerifier()
    snapshot = DOMSnapshot(
        url="https://example.com/facts",
        status_code=200,
        content_hash="mockhash123",
        raw_html="<html><body>Release date was October 13, 2026.</body></html>",
        cleaned_text="Release date was October 13, 2026.",
        timestamp_utc="2026-10-13T00:00:00Z"
    )

    status, prov = verifier.verify("October 13, 2026", snapshot)
    assert status == VerificationStatus.VERIFIED
    assert prov is not None
    assert prov.verbatim_text == "October 13, 2026"
    assert prov.snapshot_hash == "mockhash123"

def test_verifier_fails_closed_on_hallucination():
    verifier = FailClosedVerifier()
    snapshot = DOMSnapshot(
        url="https://example.com/facts",
        status_code=200,
        content_hash="mockhash123",
        raw_html="<html><body>Price is 100 USD.</body></html>",
        cleaned_text="Price is 100 USD.",
        timestamp_utc="2026-10-13T00:00:00Z"
    )

    # Fabricated answer not present in text
    status, prov = verifier.verify("Price is 999 USD", snapshot)
    assert status == VerificationStatus.REJECTED_UNVERIFIED
    assert prov is None
