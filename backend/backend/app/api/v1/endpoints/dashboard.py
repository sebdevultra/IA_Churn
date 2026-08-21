from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.dashboard import DashboardSummaryResponse
from backend.app.repositories.analytics_repo import AnalyticsRepository

router = APIRouter()


@router.get("", response_model=DashboardSummaryResponse)
def get_dashboard_data(
    db: Session = Depends(get_db)
):
    """
    Returns unified aggregated payload powering the real-time executive dashboard.
    Includes KPIs, charts data, critical alerts, and customer risk table.
    """
    return AnalyticsRepository.get_dashboard_summary(db)
