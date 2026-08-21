from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CustomerBase(BaseModel):
    external_id: str = Field(..., description="Unique customer external identifier (e.g. CUST-1001)")
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    tier: str = Field(default="standard", description="standard, pro, enterprise")


class CustomerCreate(CustomerBase):
    historical_summary: Optional[str] = ""


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    tier: Optional[str] = None
    historical_summary: Optional[str] = None


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    historical_summary: str
    current_risk_score: int
    current_risk_level: str
    last_interaction_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class CustomerDetailResponse(CustomerResponse):
    recent_interactions_count: int = 0
    open_alerts_count: int = 0
