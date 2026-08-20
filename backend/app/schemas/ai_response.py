from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class FrictionItem(BaseModel):
    category: str = Field(
        ...,
        description="Friction category: customer_support, product_reliability, pricing, usability, billing, onboarding, performance, other"
    )
    description: str = Field(..., description="Brief description of the specific friction or pain point")
    severity: str = Field(default="medium", description="Severity of the issue: low, medium, high")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid = {
            "customer_support", "product_reliability", "pricing",
            "usability", "billing", "onboarding", "performance", "other"
        }
        v_clean = v.strip().lower()
        if v_clean not in valid:
            return "other"
        return v_clean


class AIAnalysisOutput(BaseModel):
    """
    Strict Structured Output Contract expected from LLM analysis.
    Validated deterministically through Pydantic.
    """
    sentiment: str = Field(..., description="General sentiment: positive, neutral, negative")
    emotion: str = Field(..., description="Dominant emotion: joy, satisfaction, neutral, frustration, anger, disappointment")
    friction_points: List[FrictionItem] = Field(default_factory=list, description="Extracted friction points or operational bottlenecks")
    churn_intent: bool = Field(default=False, description="Whether the customer explicitly or strongly implies intent to churn/cancel")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score between 0.0 and 1.0")
    evidence: List[str] = Field(default_factory=list, description="Exact quotes or text excerpts from the customer supporting the findings")

    @field_validator("sentiment")
    @classmethod
    def validate_sentiment(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in {"positive", "neutral", "negative"}:
            return "neutral"
        return v_clean

    @field_validator("emotion")
    @classmethod
    def validate_emotion(cls, v: str) -> str:
        v_clean = v.strip().lower()
        valid = {"joy", "satisfaction", "neutral", "frustration", "anger", "disappointment"}
        if v_clean not in valid:
            return "neutral"
        return v_clean


class AIContextInput(BaseModel):
    """
    Optimized context representation sent to the LLM to minimize token consumption.
    """
    customer_id: str
    tier: str = "standard"
    historical_summary: str = ""
    previous_sentiment: Optional[str] = None
    previous_risk_score: Optional[int] = None
    recurrent_frictions: List[str] = Field(default_factory=list)
    recent_interactions_count: int = 0
