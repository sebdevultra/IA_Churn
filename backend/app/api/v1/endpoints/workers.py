from fastapi import APIRouter
from backend.app.workers.scheduler import trigger_immediate_job

router = APIRouter()


@router.post("/trigger", response_model=dict)
def trigger_ingestion_now():
    """
    Manually triggers the background ingestion and retry worker on demand.
    """
    result = trigger_immediate_job()
    return {
        "message": "Ingestion job executed",
        "result": result
    }
