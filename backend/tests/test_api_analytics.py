import pytest
from fastapi import status


def test_analytics_endpoints(client):
    """Tests all /analytics endpoints: /sentiment, /frictions, /churn, /metrics."""
    # 1. Ingest an interaction first to populate analytics
    payload = {
        "customer_external_id": "CUST-TEST-01",
        "source_type": "support_ticket",
        "content": "Pésimo servicio y lentitud en soporte.",
        "external_reference_id": "TICK-ANALYTICS-01"
    }
    client.post("/api/v1/interactions", json=payload)

    # 2. GET /analytics/sentiment
    res_sent = client.get("/api/v1/analytics/sentiment")
    assert res_sent.status_code == status.HTTP_200_OK
    data_sent = res_sent.json()
    assert "distribution" in data_sent
    assert "emotions" in data_sent
    assert "evolution" in data_sent

    # 3. GET /analytics/frictions
    res_fric = client.get("/api/v1/analytics/frictions")
    assert res_fric.status_code == status.HTTP_200_OK
    assert isinstance(res_fric.json(), list)

    # 4. GET /analytics/churn
    res_churn = client.get("/api/v1/analytics/churn")
    assert res_churn.status_code == status.HTTP_200_OK
    data_churn = res_churn.json()
    assert "low" in data_churn
    assert "critical" in data_churn

    # 5. GET /analytics/metrics
    res_metrics = client.get("/api/v1/analytics/metrics")
    assert res_metrics.status_code == status.HTTP_200_OK
    data_metrics = res_metrics.json()
    assert "total_processed" in data_metrics
    assert "estimated_ai_cost_usd" in data_metrics

    # 6. POST /workers/trigger
    res_worker = client.post("/api/v1/workers/trigger")
    assert res_worker.status_code == status.HTTP_200_OK
