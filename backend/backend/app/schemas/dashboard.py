from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.analytics import (
    SentimentDistribution,
    EmotionDistribution,
    SentimentEvolutionPoint,
    FrictionPointMetric,
    ChurnDistribution
)
from backend.app.schemas.alert import AlertResponse


class DashboardKPIs(BaseModel):
    total_customers: int
    total_interactions: int
    positive_sentiment_count: int
    neutral_sentiment_count: int
    negative_sentiment_count: int
    high_risk_customers_count: int
    critical_risk_customers_count: int
    open_alerts_count: int


class CustomerTableRow(BaseModel):
    customer_id: int
    external_id: str
    name: str
    tier: str
    last_interaction_date: Optional[datetime] = None
    last_sentiment: Optional[str] = "N/A"
    last_emotion: Optional[str] = "N/A"
    current_risk_score: int
    current_risk_level: str
    has_active_alert: bool


class DashboardSummaryResponse(BaseModel):
    kpis: DashboardKPIs
    sentiment_evolution: List[SentimentEvolutionPoint]
    sentiment_distribution: SentimentDistribution
    emotion_distribution: EmotionDistribution
    top_frictions: List[FrictionPointMetric]
    churn_distribution: ChurnDistribution
    critical_alerts: List[AlertResponse]
    recent_customers: List[CustomerTableRow]
    last_updated_at: datetime
