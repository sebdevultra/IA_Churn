from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class SentimentDistribution(BaseModel):
    positive: int
    neutral: int
    negative: int
    total: int


class EmotionDistribution(BaseModel):
    joy: int
    satisfaction: int
    neutral: int
    frustration: int
    anger: int
    disappointment: int
    other: int


class SentimentEvolutionPoint(BaseModel):
    date: str
    positive: int
    neutral: int
    negative: int
    avg_risk_score: float


class FrictionPointMetric(BaseModel):
    category: str
    count: int
    percentage: float
    high_severity_count: int


class ChurnDistribution(BaseModel):
    low: int
    medium: int
    high: int
    critical: int
    total: int


class PipelineMetricsResponse(BaseModel):
    total_processed: int
    total_successful: int
    total_failed: int
    total_duplicates_filtered: int
    total_alerts_generated: int
    avg_processing_time_ms: float
    max_processing_time_ms: float
    success_rate_percentage: float
    total_prompt_tokens: int
    total_completion_tokens: int
    estimated_ai_cost_usd: float
