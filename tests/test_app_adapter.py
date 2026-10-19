import json

from app.app import main


def test_adapter_writes_valid_empty_output_without_seed_url(tmp_path):
    assert main([
        "--query-id", "q1",
        "--query", "What is the price of Widget Pro?",
        "--output-dir", str(tmp_path),
    ]) == 0

    payload = json.loads((tmp_path / "q1_output.json").read_text())
    assert payload["answer"] == ""
    assert payload["sources"] == []
    assert payload["confidence"] == 0.0


def test_adapter_accepts_warmup_noop():
    assert main(["--warmup"]) == 0
