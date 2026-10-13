import json
from typing import List
from ..models.schema import ProvenanceRecord

class ProvenanceTracker:
    """
    Cryptographic provenance log aggregator.
    """

    def __init__(self):
        self.records: List[ProvenanceRecord] = []

    def log_record(self, record: ProvenanceRecord):
        self.records.append(record)

    def export_bundle(self) -> str:
        return json.dumps([r.model_dump() for r in self.records], indent=2)
