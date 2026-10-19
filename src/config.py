from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    max_navigation_hops: int = Field(default=5, description="Maximum navigation steps before terminating")
    request_timeout_seconds: float = Field(default=15.0, description="HTTP request timeout per step")
    max_dom_char_length: int = Field(default=100000, description="Truncation limit for DOM extraction")
    verification_threshold: float = Field(default=0.85, description="Minimum confidence for fuzzy grounding")
    max_candidates_per_page: int = Field(default=8, description="Maximum ranked candidates verified per page")
    user_agent: str = Field(
        default="InnerOS-AMD-MC4-WebRetrieval/0.2 (+https://github.com/Rafa-Innerchispa)",
        description="Polite crawler user-agent header",
    )
    rocm_device_id: int = Field(default=0, description="Target AMD GPU device index")
    allow_external_domains: bool = Field(
        default=False,
        description="Allow navigation outside the seed domain. Disabled by default.",
    )


DEFAULT_CONFIG = AgentConfig()
