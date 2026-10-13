import os
from pydantic import BaseModel, Field

class AgentConfig(BaseModel):
    max_navigation_hops: int = Field(default=5, description="Maximum navigation steps before terminating")
    request_timeout_seconds: float = Field(default=15.0, description="HTTP request timeout per step")
    max_dom_char_length: int = Field(default=100000, description="Truncation limit for raw DOM extraction")
    verification_threshold: float = Field(default=0.85, description="Minimum confidence for fuzzy match verification")
    user_agent: str = Field(
        default="AMDAILeague-MC4-WebRetrievalAgent/0.1 (+https://github.com/Rafa-Innerchispa)",
        description="Polite crawler user-agent header"
    )
    rocm_device_id: int = Field(default=0, description="Target AMD GPU device index")
    allow_external_domains: bool = Field(default=False, description="Strict domain lock to prevent crawling the wild web")

DEFAULT_CONFIG = AgentConfig()
