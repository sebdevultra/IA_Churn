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
    Returns all analyzed customer interaction cases formatted for Horizon UI.
    Lists every interaction with its individual risk score, emotion, evidence, and alert status.
    """
    interactions = (
        db.query(Interaction)
        .join(Customer)
        .order_by(desc(Interaction.created_at), desc(Interaction.id))
        .all()
    )

    cases = []
    for it in interactions:
        cust = it.customer
        r = it.churn_risk

        alert = None
        if r:
            alert = (
                db.query(Alert)
                .filter(Alert.churn_risk_id == r.id)
                .first()
            )

        factors = []
        if r and r.score_breakdown:
            sb = r.score_breakdown
            if isinstance(sb, dict):
                for k, v in sb.items():
                    factors.append({"factor": k.replace("_", " ").title(), "impact": int(v) if isinstance(v, (int, float)) else 10})
            elif isinstance(sb, list):
                for item in sb:
                    if isinstance(item, dict):
                        factor_name = item.get("reason") or item.get("factor") or item.get("rule_name", "Factor de Riesgo").replace("_", " ").title()
                        impact_val = int(item.get("impact", item.get("weight", 10)))
                        factors.append({"factor": factor_name, "impact": impact_val})
                    elif isinstance(item, str):
                        factors.append({"factor": item, "impact": 10})

        risk_score = int(r.risk_score) if r else 0
        risk_level = r.risk_level if r else "LOW"

        if not factors:
            factors = [
                {"factor": f"Riesgo {risk_level.upper()}", "impact": max(5, int(risk_score * 0.4))},
                {"factor": f"Cliente Tier {cust.tier}", "impact": 20 if (cust.tier and cust.tier.lower() == "enterprise") else 10}
            ]

        emotion = "neutral"
        friction = "customer_support"
        raw_text = it.content if it.content else "Sin evidencia textual registrada."
        masked_text = raw_text

        if it.sentiment:
            s = it.sentiment
            emotion = s.emotion or "neutral"
            ai_engine = s.model_name or "local_nlp"
            if s.evidence and len(s.evidence) > 0:
                masked_text = s.evidence[0]
        else:
            ai_engine = "local_nlp"

        if it.frictions and len(it.frictions) > 0:
            friction = it.frictions[0].category or "customer_support"

        if alert:
            if alert.status in ["NEW", "PENDING"]:
                status_str = "PENDING"
            elif alert.status in ["ACKNOWLEDGED", "IN_REVIEW"]:
                status_str = "IN_REVIEW"
            elif alert.status in ["RESOLVED", "CLOSED"]:
                status_str = "RESOLVED"
            else:
                status_str = alert.status
        else:
            status_str = "PENDING" if risk_score >= 60 else "RESOLVED"

        case_id = f"ALT-{alert.id}" if alert else f"INT-{it.id}"

        cases.append({
            "id": case_id,
            "db_alert_id": alert.id if alert else None,
            "interaction_id": it.id,
            "customerName": cust.name,
            "tier": cust.tier or "Standard",
            "riskScore": risk_score,
            "emotion": emotion,
            "friction": friction,
            "rawEvidence": raw_text,
            "maskedEvidence": masked_text,
            "status": status_str,
            "aiEngine": ai_engine,
            "scoreFactors": factors,
            "timestamp": it.created_at.isoformat() if it.created_at else ""
        })

    return {"success": True, "data": cases}
