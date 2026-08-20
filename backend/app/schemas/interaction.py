from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class InteractionCreate(BaseModel):
    customer_external_id: str = Field(..., description="External customer ID (e.g. CUST-1001)")
    source_type: str = Field(..., description="Source: support_ticket, review, survey, chat")
    content: str = Field(..., min_length=1, max_length=10000, description="Raw feedback or interaction text")
    external_reference_id: Optional[str] = Field(None, description="External ticket ID or review UUID")

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Interaction content cannot be empty or contain only whitespace.")
        return v.strip()

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        valid = {"support_ticket", "review", "survey", "chat", "email"}
        v_clean = v.strip().lower()
        if v_clean not in valid:
            return "support_ticket"
        return v_clean


class SentimentAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sentiment: str
    emotion: str
    churn_intent: bool
    confidence: float
    evidence: List[str]
    model_name: Optional[str]
    prompt_tokens: int
    completion_tokens: int
    created_at: datetime


class FrictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    description: str
    severity: str


class ChurnRiskSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    risk_score: int
    risk_level: str
    calculated_at: datetime


class InteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    customer_external_id: Optional[str] = None
    source_type: str
    content: str
    interaction_hash: str
    external_reference_id: Optional[str]
    status: str
    retry_count: int
    error_message: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    sentiment: Optional[SentimentAnalysisResponse] = None
    frictions: List[FrictionResponse] = []
    churn_risk: Optional[ChurnRiskSummary] = None


class InteractionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[InteractionResponse]
