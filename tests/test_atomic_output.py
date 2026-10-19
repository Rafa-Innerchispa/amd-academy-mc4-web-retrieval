import json

from src.io.atomic_output import initialize_empty_output, write_json_atomic


def test_atomic_output_roundtrip(tmp_path):
    target = tmp_path / "q_output.json"
    initialize_empty_output(target)
    assert json.loads(target.read_text()) == {
        "answer": "",
        "sources": [],
        "confidence": 0.0,
    }

    write_json_atomic(
        target,
        {
            "answer": "42",
            "sources": ["https://example.com"],
            "confidence": 1.0,
        },
    )

    assert json.loads(target.read_text())["answer"] == "42"
    assert not list(tmp_path.glob("*.tmp"))
