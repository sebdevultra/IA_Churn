from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class AlertUpdateStatus(BaseModel):
    status: str = Field(..., description="Target status: NEW, ACKNOWLEDGED, IN_REVIEW, PENDING, RESOLVED")
    user_name: Optional[str] = Field(default="Analyst User", description="Name of the team member acknowledging/resolving")
    resolution_notes: Optional[str] = Field(None, description="Notes on how the churn risk was addressed or contacted")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        v_clean = v.strip().upper()
        if v_clean == "IN_REVIEW":
            v_clean = "ACKNOWLEDGED"
        valid = {"NEW", "ACKNOWLEDGED", "RESOLVED", "PENDING", "IN_REVIEW"}
        if v_clean not in valid:
            raise ValueError(f"Status must be one of: {', '.join(valid)}")
        return v_clean


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    customer_external_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_tier: Optional[str] = None
    churn_risk_id: int
    severity: str
    title: str
    reasons: List[str]
    status: str
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AlertListResponse(BaseModel):
    total: int
    items: List[AlertResponse]
