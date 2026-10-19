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


def test_adapter_accepts_short_query_alias(tmp_path):
    assert main([
        "--query-id", "q-short",
        "-q", "What is the price of Widget Pro?",
        "--output-dir", str(tmp_path),
    ]) == 0
    payload = json.loads((tmp_path / "q-short_output.json").read_text())
    assert payload["answer"] == ""


def test_adapter_accepts_input_file_and_tasks_aliases(tmp_path):
    batch = tmp_path / "tasks.json"
    batch.write_text(json.dumps([
        {"id": "q-batch", "question": "What is the price of Widget Pro?"}
    ]))

    output_a = tmp_path / "out-a"
    assert main(["--input-file", str(batch), "--output-dir", str(output_a)]) == 0
    assert (output_a / "q-batch_output.json").exists()

    output_b = tmp_path / "out-b"
    assert main(["--tasks", str(batch), "--output-dir", str(output_b)]) == 0
    assert (output_b / "q-batch_output.json").exists()


def test_adapter_accepts_single_task_json_object(tmp_path):
    batch = tmp_path / "single.json"
    batch.write_text(json.dumps({
        "query_id": "q-single",
        "query": "What is the price of Widget Pro?"
    }))

    output = tmp_path / "single-out"
    assert main(["--input", str(batch), "--output-dir", str(output)]) == 0
    payload = json.loads((output / "q-single_output.json").read_text())
    assert payload["answer"] == ""


def test_index_is_noop_only_when_no_query_is_present(tmp_path):
    assert main(["--index", "/unused"]) == 0

    assert main([
        "--index", "/unused",
        "--query-id", "q-index-query",
        "--query", "What is the price of Widget Pro?",
        "--output-dir", str(tmp_path),
    ]) == 0
    assert (tmp_path / "q-index-query_output.json").exists()
