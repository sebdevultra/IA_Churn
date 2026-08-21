from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskWeightsConfig:
    """
    Centralized, fully configurable deterministic weights for Churn Risk Calculation.
    These weights are purely deterministic and calculated in Python.
    """
    # Sentiment weights
    SENTIMENT_NEGATIVE: int = 20
    SENTIMENT_NEUTRAL: int = 0
    SENTIMENT_POSITIVE: int = -10  # Positive sentiment reduces existing churn risk

    # Emotion weights
    EMOTION_FRUSTRATION: int = 20
    EMOTION_ANGER: int = 25
    EMOTION_DISAPPOINTMENT: int = 15
    EMOTION_NEUTRAL: int = 0
    EMOTION_SATISFACTION: int = -5
    EMOTION_JOY: int = -10

    # Churn Intent Weight
    CHURN_INTENT_EXPLICIT: int = 30

    # Historical & Recurrence Weights
    RECURRENT_FRICTION_ISSUE: int = 15  # Customer has had same friction in prior interactions
    FRICTION_SUPPORT_ISSUE: int = 10     # Friction is specifically related to customer support
    RECENT_NEGATIVE_SIGNAL: int = 5      # Another negative interaction occurred within last 7 days

    # Enterprise Tier Multiplier (Enterprise clients carry higher business risk)
    TIER_ENTERPRISE_MULTIPLIER: float = 1.1
    TIER_STANDARD_MULTIPLIER: float = 1.0
    ENTERPRISE_SARCASM_MIN_SCORE: int = 80  # Sarcasm in Enterprise accounts carries minimum 80 pts (Critical Risk)

    # Confidence Threshold (if LLM confidence is low, weight impact is proportionally dampener)
    MIN_CONFIDENCE_THRESHOLD: float = 0.50

    # Score Range
    MIN_SCORE: int = 0
    MAX_SCORE: int = 100

    # Level thresholds
    THRESHOLD_LOW_MAX: int = 29
    THRESHOLD_MEDIUM_MAX: int = 59
    THRESHOLD_HIGH_MAX: int = 79
    THRESHOLD_CRITICAL_MIN: int = 80


def get_risk_level_from_score(score: int) -> RiskLevel:
    """Classifies risk score into LOW, MEDIUM, HIGH, or CRITICAL."""
    if score >= RiskWeightsConfig.THRESHOLD_CRITICAL_MIN:
        return RiskLevel.CRITICAL
    elif score > RiskWeightsConfig.THRESHOLD_MEDIUM_MAX:
        return RiskLevel.HIGH
    elif score > RiskWeightsConfig.THRESHOLD_LOW_MAX:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


class ScoreFactor(BaseModel):
    rule_name: str
    weight: int
    applied: bool
    reason: str


class RiskCalculationResult(BaseModel):
    raw_score: int
    final_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    breakdown: List[ScoreFactor]
    summary_reasons: List[str]
    is_critical: bool
