from src.models.schema import DOMSnapshot, VerificationStatus
from src.verifier.fail_closed_verifier import FailClosedVerifier


def test_verifier_accepts_value_grounded_only_in_raw_html_json_ld():
    verifier = FailClosedVerifier()
    snapshot = DOMSnapshot(
        url="https://example.com/product",
        status_code=200,
        content_hash="hash-jsonld",
        raw_html='<script type="application/ld+json">{"price":"$349.00"}</script><h1>Widget Pro</h1>',
        cleaned_text="Widget Pro",
        timestamp_utc="2026-10-19T00:00:00Z",
    )

    status, provenance = verifier.verify("$349.00", snapshot)

    assert status == VerificationStatus.VERIFIED
    assert provenance is not None
    assert provenance.coordinate_space == "raw_html"
    assert provenance.verbatim_text == "$349.00"
