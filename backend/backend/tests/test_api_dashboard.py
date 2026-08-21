import pytest
from fastapi import status


def test_api_dashboard_endpoint(client):
    """Verifies that GET /dashboard returns complete summary structure."""
    response = client.get("/api/v1/dashboard")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "kpis" in data
    assert "sentiment_evolution" in data
    assert "sentiment_distribution" in data
    assert "emotion_distribution" in data
    assert "top_frictions" in data
    assert "churn_distribution" in data
    assert "critical_alerts" in data
    assert "recent_customers" in data
    assert data["kpis"]["total_customers"] >= 2


def test_api_health_check(client):
    """Verifies GET /health endpoint returns healthy status and DB ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "ok"
    assert "ai_provider" in data
