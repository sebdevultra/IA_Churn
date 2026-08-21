from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.workers.scheduler import scheduler

router = APIRouter()


@router.get("", response_model=dict)
def health_check(
    db: Session = Depends(get_db)
):
    """
    Returns system health status, DB connectivity, AI provider config, and scheduler state.
    """
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "ai_provider": settings.AI_PROVIDER,
        "scheduler": {
            "running": scheduler.running,
            "jobs_count": len(scheduler.get_jobs()) if scheduler.running else 0
        },
        "version": "1.0.0"
    }
