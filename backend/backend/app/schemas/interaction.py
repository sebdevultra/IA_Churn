from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class InteractionCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    customer_external_id: Optional[str] = Field(None, description="External customer ID (e.g. CUST-1001)")
    customerName: Optional[str] = Field(None, description="Alternative customer name/id from frontend simulator")
    customer_name: Optional[str] = None
    customer_id: Optional[str] = None

    source_type: str = Field(default="support_ticket", description="Source: support_ticket, review, survey, chat")
    content: Optional[str] = Field(None, description="Raw feedback or interaction text")
    text: Optional[str] = None
    message: Optional[str] = None

    external_reference_id: Optional[str] = Field(None, description="External ticket ID or review UUID")
    tier: Optional[str] = Field(default="Standard", description="Customer tier: Enterprise, Pro, Standard")
    customer_tier: Optional[str] = None
    aiEngine: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def unify_and_validate_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # Resolve content from text / message
            content_val = values.get("content") or values.get("text") or values.get("message")
            if not content_val or not str(content_val).strip():
                raise ValueError("Interaction content cannot be empty or contain only whitespace.")
            values["content"] = str(content_val).strip()

            # Resolve customer_external_id
            if not values.get("customer_external_id"):
                values["customer_external_id"] = (
                    values.get("customer_id") or
                    values.get("customerName") or
                    values.get("customer_name") or
                    "CUST-SIMULATED"
                )

            # Resolve tier
            if not values.get("tier"):
                values["tier"] = values.get("customer_tier") or "Standard"

            # Resolve source_type
            if not values.get("source_type"):
                values["source_type"] = "support_ticket"

        return values

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        valid = {"support_ticket", "review", "survey", "chat", "email"}
        v_clean = (v or "support_ticket").strip().lower()
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
