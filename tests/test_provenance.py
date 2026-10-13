import json
from src.provenance.tracker import ProvenanceTracker
from src.models.schema import ProvenanceRecord

def test_provenance_logging_and_export():
    tracker = ProvenanceTracker()
    record = ProvenanceRecord(
        snapshot_hash="abcde12345",
        source_url="https://amd.com/rocm",
        char_offset_start=10,
        char_offset_end=25,
        verbatim_text="ROCm 6.2 Release",
        timestamp_utc="2026-10-13T12:00:00Z"
    )
    tracker.log_record(record)
    assert len(tracker.records) == 1

    bundle_json = tracker.export_bundle()
    data = json.loads(bundle_json)
    assert len(data) == 1
    assert data[0]["snapshot_hash"] == "abcde12345"
    assert data[0]["verbatim_text"] == "ROCm 6.2 Release"
