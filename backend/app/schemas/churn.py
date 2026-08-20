from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.core.risk_rules import RiskLevel


class ChurnRiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    interaction_id: int
    risk_score: int
    risk_level: RiskLevel
    score_breakdown: List[Dict[str, Any]]
    calculated_at: datetime


class ChurnTrendPoint(BaseModel):
    date: str
    avg_risk_score: float
    high_risk_count: int
    critical_risk_count: int
