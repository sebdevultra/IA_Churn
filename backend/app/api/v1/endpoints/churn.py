from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.session import get_db
from backend.app.models.churn_risk import ChurnRisk
from backend.app.models.customer import Customer
from backend.app.models.interaction import Interaction
from backend.app.models.alert import Alert

router = APIRouter()


@router.get("/high-risk", response_model=dict)
def get_high_risk_cases_for_horizon_ui(db: Session = Depends(get_db)):
    """
    Returns high-risk and critical customer churn cases formatted for Horizon UI.
    """
    churn_records = (
        db.query(ChurnRisk)
        .join(Customer)
        .order_by(desc(ChurnRisk.risk_score), desc(ChurnRisk.calculated_at))
        .limit(30)
        .all()
    )

    cases = []
    for r in churn_records:
        cust = r.customer
        last_it = (
            db.query(Interaction)
            .filter(Interaction.customer_id == cust.id)
            .order_by(desc(Interaction.created_at))
            .first()
        )

        alert = (
            db.query(Alert)
            .filter(Alert.churn_risk_id == r.id)
            .first()
        )

        factors = []
        sb = r.score_breakdown
        if isinstance(sb, dict):
            for k, v in sb.items():
                factors.append({"factor": k.replace("_", " ").title(), "impact": int(v) if isinstance(v, (int, float)) else 10})
        elif isinstance(sb, list):
            for item in sb:
                if isinstance(item, dict):
                    factors.append({"factor": item.get("factor", "Factor").replace("_", " ").title(), "impact": int(item.get("impact", item.get("weight", 10)))})
                elif isinstance(item, str):
                    factors.append({"factor": item, "impact": 10})

        if not factors:
            factors = [
                {"factor": f"Riesgo {r.risk_level.upper()}", "impact": int(r.risk_score * 0.4)},
                {"factor": f"Cliente Tier {cust.tier}", "impact": 20 if cust.tier == "Enterprise" else 10}
            ]

        emotion = "neutral"
        friction = "customer_support"
        raw_text = last_it.content if last_it else "Sin evidencia textual registrada."
        masked_text = raw_text

        if last_it and last_it.sentiment:
            s = last_it.sentiment
            emotion = s.emotion or "neutral"
            ai_engine = s.model_name or "deterministic_rule"
        else:
            ai_engine = "deterministic_rule"

        if last_it and last_it.frictions:
            friction = last_it.frictions[0].category or "customer_support"

        status_str = alert.status if alert else ("PENDING" if r.risk_score >= 60 else "RESOLVED")

        cases.append({
            "id": f"ALT-{alert.id}" if alert else f"RSK-{r.id}",
            "db_alert_id": alert.id if alert else None,
            "customerName": cust.name,
            "tier": cust.tier,
            "riskScore": int(r.risk_score),
            "emotion": emotion,
            "friction": friction,
            "rawEvidence": raw_text,
            "maskedEvidence": masked_text,
            "status": status_str,
            "aiEngine": ai_engine,
            "scoreFactors": factors,
            "timestamp": r.calculated_at.isoformat() if r.calculated_at else ""
        })

    return {"success": True, "data": cases}
