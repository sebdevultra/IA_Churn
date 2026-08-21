from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.models.alert import Alert
from backend.app.models.customer import Customer
from backend.app.models.churn_risk import ChurnRisk
from backend.app.core.risk_rules import RiskCalculationResult, RiskLevel
from backend.app.core.errors import ResourceNotFoundError, InvalidStateTransitionError
from backend.app.schemas.alert import AlertUpdateStatus
from backend.app.core.logging import logger


class AlertService:
    """
    Automated Alert Engine for High & Critical Churn Risk events.
    """

    @classmethod
    def evaluate_and_create_alert(
        cls,
        db: Session,
        customer: Customer,
        churn_risk: ChurnRisk,
        risk_result: RiskCalculationResult
    ) -> Optional[Alert]:
        """
        Creates a critical/high alert if the score reaches High (>=60) or Critical (>=80).
        Avoids spamming if an active (NEW/ACKNOWLEDGED/IN_REVIEW/PENDING) alert already exists for this customer.
        """
        if risk_result.final_score < 60:
            return None

        # Check if customer already has a pending/open alert
        existing_open_alert = (
            db.query(Alert)
            .filter(
                Alert.customer_id == customer.id,
                Alert.status.in_(["NEW", "ACKNOWLEDGED", "IN_REVIEW", "PENDING"])
            )
            .first()
        )

        title = f"ALERTA {risk_result.risk_level.value}: Riesgo de Churn ({risk_result.final_score}/100) - {customer.name}"

        if existing_open_alert:
            existing_open_alert.churn_risk_id = churn_risk.id
            existing_open_alert.severity = risk_result.risk_level.value
            existing_open_alert.title = title
            existing_open_alert.reasons = risk_result.summary_reasons
            existing_open_alert.updated_at = datetime.utcnow()
            logger.info(f"Updated existing open alert #{existing_open_alert.id} for Customer {customer.external_id}")
            return existing_open_alert

        # Create new Alert
        alert = Alert(
            customer_id=customer.id,
            churn_risk_id=churn_risk.id,
            severity=risk_result.risk_level.value,
            title=title,
            reasons=risk_result.summary_reasons,
            status="PENDING",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(alert)
        db.flush()
        logger.warning(f"CHURN ALERT CREATED for Customer #{customer.id} ({customer.external_id}) - Score: {risk_result.final_score}/100")
        return alert

    @classmethod
    def update_alert_status(
        cls,
        db: Session,
        alert_id: int,
        update_data: AlertUpdateStatus
    ) -> Alert:
        """
        Transitions alert state: PENDING / NEW <-> IN_REVIEW / ACKNOWLEDGED <-> RESOLVED.
        Allows flexible bidirectional updates from the CSM intervention console.
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise ResourceNotFoundError(resource_name="Alert", resource_id=alert_id)

        raw_status = (update_data.status or "PENDING").upper().strip()
        if raw_status in ["IN_REVIEW", "IN-REVIEW", "IN REVIEW", "REVIEW", "ACKNOWLEDGED"]:
            target_status = "IN_REVIEW"
        elif raw_status in ["RESOLVED", "RESOLVE", "CLOSED", "RESUELTO"]:
            target_status = "RESOLVED"
        else:
            target_status = "PENDING"

        alert.status = target_status
        alert.updated_at = datetime.utcnow()

        if target_status == "IN_REVIEW":
            alert.acknowledged_by = update_data.user_name or "CSM Lead"
            if update_data.resolution_notes:
                alert.resolution_notes = update_data.resolution_notes
        elif target_status == "RESOLVED":
            alert.resolved_by = update_data.user_name or "CSM Lead"
            if update_data.resolution_notes:
                alert.resolution_notes = update_data.resolution_notes
        elif target_status == "PENDING":
            alert.acknowledged_by = None
            alert.resolved_by = None

        db.commit()
        db.refresh(alert)
        logger.info(f"Alert #{alert.id} transitioned to {target_status} by {update_data.user_name or 'User'}")
        return alert
