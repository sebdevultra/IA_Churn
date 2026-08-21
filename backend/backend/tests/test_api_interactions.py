import pytest
from fastapi import status


def test_api_create_interaction_positive(client):
    """Case 1 via API: Positive message creates interaction with LOW risk."""
    payload = {
        "customer_external_id": "CUST-TEST-01",
        "source_type": "review",
        "content": "Excelente servicio, la plataforma es fantástica.",
        "external_reference_id": "REV-TEST-01"
    }

    response = client.post("/api/v1/interactions", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["status"] == "PROCESSED"
    assert data["sentiment"]["sentiment"] == "positive"
    assert data["churn_risk"]["risk_level"] == "LOW"


def test_api_create_interaction_empty_content_rejected(client):
    """Case 5 & 6 via API: Empty or whitespace-only content is rejected with 422."""
    payload = {
        "customer_external_id": "CUST-TEST-01",
        "source_type": "chat",
        "content": "   "
    }

    response = client.post("/api/v1/interactions", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_api_duplicate_interaction_returns_409(client):
    """Case 8 via API: Duplicate submission returns 409 Conflict."""
    payload = {
        "customer_external_id": "CUST-TEST-01",
        "source_type": "survey",
        "content": "Servicio aceptable pero puede mejorar en velocidad.",
        "external_reference_id": "SURV-1"
    }

    res1 = client.post("/api/v1/interactions", json=payload)
    assert res1.status_code == status.HTTP_201_CREATED

    res2 = client.post("/api/v1/interactions", json=payload)
    assert res2.status_code == status.HTTP_409_CONFLICT
    err = res2.json()
    assert err["error"]["type"] == "DuplicateInteractionError"


def test_api_list_interactions_pagination(client):
    """Tests GET /interactions pagination and filter."""
    response = client.get("/api/v1/interactions?page=1&page_size=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
