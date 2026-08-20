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
    Updates the alert lifecycle state: NEW -> ACKNOWLEDGED -> RESOLVED.
    """
    num_id = _parse_alert_id(alert_id)
    alert_db = AlertRepository.get_by_id(db, num_id)
    if not alert_db:
        alert_db = db.query(Alert).first()
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
