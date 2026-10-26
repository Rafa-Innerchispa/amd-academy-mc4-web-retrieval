from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    REJECTED_UNVERIFIED = "REJECTED_UNVERIFIED"
    EVIDENCE_MISSING = "EVIDENCE_MISSING"


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language retrieval request")
    seed_url: Optional[str] = Field(None, description="Starting URL if specified")
    max_hops: Optional[int] = Field(5, ge=1, le=12, description="Maximum navigation hops")


class ParsedIntent(BaseModel):
    raw_query: str
    target_entity: str
    target_attribute: str
    inferred_seed_url: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)


class DOMSnapshot(BaseModel):
    url: str
    status_code: int
    content_hash: str = Field(..., description="SHA-256 hash of raw HTML")
    raw_html: str
    cleaned_text: str
    timestamp_utc: str


class NavigationStep(BaseModel):
    step_number: int
    action: str = Field(..., description="VISIT_URL or FOLLOW_LINK")
    target_url: str
    reason: str


class ProvenanceRecord(BaseModel):
    snapshot_hash: str
    source_url: str
    char_offset_start: int
    char_offset_end: int
    verbatim_text: str
    timestamp_utc: str
    coordinate_space: str = Field(default="cleaned_text", description="cleaned_text or raw_html")


class RetrievalResponse(BaseModel):
    status: str = Field(..., description="SUCCESS, FAIL_CLOSED, ERROR")
    query: str
    answer: Optional[str] = None
    verification_status: VerificationStatus
    provenance: Optional[ProvenanceRecord] = None
    navigation_trail: List[NavigationStep] = Field(default_factory=list)
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
