from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    interactions,
    customers,
    alerts,
    analytics,
    dashboard,
    health,
    workers,
    churn
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(interactions.router, prefix="/interactions", tags=["Interactions"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(churn.router, prefix="/churn", tags=["Churn Risk"])
api_router.include_router(workers.router, prefix="/workers", tags=["Workers"])
