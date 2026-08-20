from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.schemas.analytics import (
    FrictionPointMetric,
    ChurnDistribution,
    PipelineMetricsResponse
)
from backend.app.repositories.analytics_repo import AnalyticsRepository
from backend.app.models.interaction import Interaction
from backend.app.models.churn_risk import ChurnRisk
from backend.app.models.customer import Customer
from backend.app.models.alert import Alert

router = APIRouter()


@router.get("/sentiment", response_model=dict)
def get_sentiment_analytics(
    days: int = Query(14, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Returns sentiment distribution, emotion distribution, and temporal evolution.
    """
    return {
        "distribution": AnalyticsRepository.get_sentiment_distribution(db),
        "emotions": AnalyticsRepository.get_emotion_distribution(db),
        "evolution": AnalyticsRepository.get_sentiment_evolution(db, days=days)
    }


@router.get("/frictions", response_model=List[FrictionPointMetric])
def get_friction_analytics(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Returns ranked friction categories with frequency percentages and severity.
    """
    return AnalyticsRepository.get_top_friction_points(db, limit=limit)


@router.get("/churn", response_model=ChurnDistribution)
def get_churn_analytics(
    db: Session = Depends(get_db)
):
    """
    Returns churn risk level distribution across the customer base.
    """
    return AnalyticsRepository.get_churn_distribution(db)


@router.get("/metrics", response_model=PipelineMetricsResponse)
def get_pipeline_execution_metrics(
    db: Session = Depends(get_db)
):
    """
    Returns processing performance metrics, token usage audits, and estimated AI costs.
    """
    return AnalyticsRepository.get_pipeline_metrics(db)


# --- Horizon UI Helper Endpoints ---

@router.get("/kpis", response_model=dict)
def get_kpis_for_horizon_ui(db: Session = Depends(get_db)):
    """
    Returns executive KPI card metrics formatted for Horizon UI.
    """
    total_interactions = db.query(func.count(Interaction.id)).scalar() or 0
    dist = AnalyticsRepository.get_sentiment_distribution(db)

    total_dist = dist.total if dist.total > 0 else 1
    pos_pct = round((dist.positive / total_dist) * 100, 1)
    neu_pct = round((dist.neutral / total_dist) * 100, 1)
    neg_pct = round((dist.negative / total_dist) * 100, 1)

    nps = int(pos_pct - neg_pct)
    nps_status = "Excelente" if nps >= 30 else ("Saludable" if nps >= 0 else "En Riesgo")

    high_count = db.query(func.count(ChurnRisk.id)).filter(ChurnRisk.risk_score >= 60, ChurnRisk.risk_score < 80).scalar() or 0
    critical_count = db.query(func.count(Alert.id)).filter(Alert.status.in_(["NEW", "PENDING"])).scalar() or 0

    return {
        "success": True,
        "data": {
            "totalInteractions": total_interactions,
            "positivePercentage": int(pos_pct),
            "neutralPercentage": int(neu_pct),
            "negativePercentage": int(neg_pct),
            "predictiveNps": nps,
            "npsStatus": nps_status,
            "highRiskCount": high_count,
            "criticalRiskCount": critical_count
        }
    }


@router.get("/sentiment-trend", response_model=dict)
def get_sentiment_trend_for_horizon_ui(days: int = 14, db: Session = Depends(get_db)):
    """
    Returns 30d/14d temporal evolution formatted for Horizon UI.
    """
    evo = AnalyticsRepository.get_sentiment_evolution(db, days=days)
    data = []
    for item in evo:
        data.append({
            "date": item.date,
            "positive": item.positive,
            "neutral": item.neutral,
            "negative": item.negative
        })

    return {"success": True, "data": data}


@router.get("/friction-distribution", response_model=dict)
def get_friction_distribution_for_horizon_ui(db: Session = Depends(get_db)):
    """
    Returns friction point counts by category formatted for Horizon UI.
    """
    frictions = AnalyticsRepository.get_top_friction_points(db, limit=20)
    data = {
        "customer_support": 0,
        "billing_pricing": 0,
        "product_reliability": 0,
        "sla_delay": 0,
        "feature_gap": 0
    }
    for item in frictions:
        cat = item.category.lower().replace(" ", "_")
        if cat in data:
            data[cat] = item.count
        else:
            data[cat] = item.count

    return {"success": True, "data": data}
