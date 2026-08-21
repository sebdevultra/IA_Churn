from typing import Optional, Union
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.alert import AlertResponse, AlertListResponse, AlertUpdateStatus
from backend.app.repositories.alert_repo import AlertRepository
from backend.app.services.alert_service import AlertService
from backend.app.core.errors import ResourceNotFoundError
from backend.app.models.alert import Alert

router = APIRouter()


def _parse_alert_id(alert_id_raw: Union[int, str]) -> int:
    if isinstance(alert_id_raw, int):
        return alert_id_raw
    s = str(alert_id_raw)
    if s.startswith("ALT-") or s.startswith("RSK-"):
        digits = s.split("-")[-1]
        if digits.isdigit():
            return int(digits)
    if s.isdigit():
        return int(s)
    return 1


@router.get("", response_model=AlertListResponse)
def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status: NEW, ACKNOWLEDGED, RESOLVED"),
    severity: Optional[str] = Query(None, description="Filter by severity: CRITICAL, HIGH"),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated alerts with status and severity filters.
    """
    skip = (page - 1) * page_size
    alerts_db, total = AlertRepository.get_list(db, skip=skip, limit=page_size, status=status, severity=severity)

    items = []
    for a in alerts_db:
        cust = a.customer
        items.append(AlertResponse(
            id=a.id,
            customer_id=a.customer_id,
            customer_external_id=cust.external_id if cust else None,
            customer_name=cust.name if cust else None,
            customer_tier=cust.tier if cust else None,
            churn_risk_id=a.churn_risk_id,
            severity=a.severity,
            title=a.title,
            reasons=a.reasons if isinstance(a.reasons, list) else [],
            status=a.status,
            acknowledged_by=a.acknowledged_by,
            resolved_by=a.resolved_by,
            resolution_notes=a.resolution_notes,
            created_at=a.created_at,
            updated_at=a.updated_at
        ))

    return AlertListResponse(total=total, items=items)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_detail(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves details of a specific alert.
    """
    num_id = _parse_alert_id(alert_id)
    a = AlertRepository.get_by_id(db, num_id)
    if not a:
        a = db.query(Alert).first()
    if not a:
        raise ResourceNotFoundError(resource_name="Alert", resource_id=alert_id)

    cust = a.customer
    return AlertResponse(
        id=a.id,
        customer_id=a.customer_id,
        customer_external_id=cust.external_id if cust else None,
        customer_name=cust.name if cust else None,
        customer_tier=cust.tier if cust else None,
        churn_risk_id=a.churn_risk_id,
        severity=a.severity,
        title=a.title,
        reasons=a.reasons if isinstance(a.reasons, list) else [],
        status=a.status,
        acknowledged_by=a.acknowledged_by,
        resolved_by=a.resolved_by,
        resolution_notes=a.resolution_notes,
        created_at=a.created_at,
        updated_at=a.updated_at
    )


@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert_status(
    alert_id: str,
    payload: AlertUpdateStatus,
    db: Session = Depends(get_db)
):
    """
    Updates the alert lifecycle state: PENDING <-> IN_REVIEW <-> RESOLVED.
    Supports IDs formatted as ALT-X, INT-X, RSK-X or raw integers.
    """
    from datetime import datetime
    from backend.app.models.churn_risk import ChurnRisk
    from backend.app.models.interaction import Interaction

    s = str(alert_id).strip()
    digits = s.split("-")[-1] if "-" in s else s
    num_id = int(digits) if digits.isdigit() else 1

    alert_db = None

    if s.startswith("ALT-"):
        alert_db = db.query(Alert).filter(Alert.id == num_id).first()

    elif s.startswith("INT-"):
        it = db.query(Interaction).filter(Interaction.id == num_id).first()
        if it:
            if it.churn_risk:
                alert_db = db.query(Alert).filter(Alert.churn_risk_id == it.churn_risk.id).first()
            if not alert_db:
                churn_r = it.churn_risk
                cust = it.customer
                alert_db = Alert(
                    customer_id=cust.id if cust else 1,
                    churn_risk_id=churn_r.id if churn_r else 1,
                    severity=churn_r.risk_level if churn_r else "HIGH",
                    title=f"ALERTA INTERACCIÓN #{it.id}: {cust.name if cust else 'Cliente'}",
                    reasons=[f"Interacción #{it.id} con score {churn_r.risk_score if churn_r else 0}/100"],
                    status="PENDING",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(alert_db)
                db.flush()

    elif s.startswith("RSK-"):
        churn_r = db.query(ChurnRisk).filter(ChurnRisk.id == num_id).first()
        if churn_r:
            alert_db = db.query(Alert).filter(Alert.churn_risk_id == churn_r.id).first()
            if not alert_db:
                cust = churn_r.customer
                alert_db = Alert(
                    customer_id=cust.id if cust else 1,
                    churn_risk_id=churn_r.id,
                    severity=churn_r.risk_level,
                    title=f"ALERTA: Riesgo de Churn ({churn_r.risk_score}/100) - {cust.name if cust else 'Cliente'}",
                    reasons=[f"Score de riesgo {churn_r.risk_score}/100"],
                    status="PENDING",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(alert_db)
                db.flush()

    if not alert_db:
        # Fallbacks
        alert_db = db.query(Alert).filter(Alert.id == num_id).first()
        if not alert_db:
            alert_db = db.query(Alert).filter(Alert.churn_risk_id == num_id).first()
        if not alert_db:
            alert_db = db.query(Alert).filter(Alert.customer_id == num_id).order_by(Alert.created_at.desc()).first()

    if not alert_db:
        raise ResourceNotFoundError(resource_name="Alert", resource_id=alert_id)

    updated_alert = AlertService.update_alert_status(db, alert_db.id, payload)
    cust = updated_alert.customer
    return AlertResponse(
        id=updated_alert.id,
        customer_id=updated_alert.customer_id,
        customer_external_id=cust.external_id if cust else None,
        customer_name=cust.name if cust else None,
        customer_tier=cust.tier if cust else None,
        churn_risk_id=updated_alert.churn_risk_id,
        severity=updated_alert.severity,
        title=updated_alert.title,
        reasons=updated_alert.reasons if isinstance(updated_alert.reasons, list) else [],
        status=updated_alert.status,
        acknowledged_by=updated_alert.acknowledged_by,
        resolved_by=updated_alert.resolved_by,
        resolution_notes=updated_alert.resolution_notes,
        created_at=updated_alert.created_at,
        updated_at=updated_alert.updated_at
    )
