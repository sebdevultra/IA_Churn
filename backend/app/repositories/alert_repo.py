from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from backend.app.models.alert import Alert


class AlertRepository:

    @staticmethod
    def get_by_id(db: Session, alert_id: int) -> Optional[Alert]:
        return (
            db.query(Alert)
            .options(joinedload(Alert.customer), joinedload(Alert.churn_risk))
            .filter(Alert.id == alert_id)
            .first()
        )

    @staticmethod
    def get_list(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        severity: Optional[str] = None
    ) -> Tuple[List[Alert], int]:
        query = db.query(Alert).options(joinedload(Alert.customer), joinedload(Alert.churn_risk))

        if status:
            query = query.filter(Alert.status == status.upper())
        if severity:
            query = query.filter(Alert.severity == severity.upper())

        total = query.count()
        items = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def get_open_alerts_count(db: Session) -> int:
        return db.query(Alert).filter(Alert.status.in_(["NEW", "ACKNOWLEDGED"])).count()
