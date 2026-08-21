import pytest
from fastapi import status


def test_critical_interaction_triggers_new_alert_and_transitions(client):
    """Case 12 & 13: Critical churn signal creates alert with status NEW, then transitions to ACKNOWLEDGED and RESOLVED."""
    payload = {
        "customer_external_id": "CUST-TEST-01",
        "source_type": "support_ticket",
        "content": "Llevamos días esperando soporte técnico y nadie responde. Es inaceptable. Voy a cancelar el contrato de inmediato.",
        "external_reference_id": "TICK-CRIT-99"
    }

    # 1. Ingest Critical Interaction
    res_it = client.post("/api/v1/interactions", json=payload)
    assert res_it.status_code == status.HTTP_201_CREATED
    it_data = res_it.json()
    assert it_data["churn_risk"]["risk_level"] == "CRITICAL"

    # 2. Check Alerts List
    res_alerts = client.get("/api/v1/alerts?status=NEW")
    assert res_alerts.status_code == status.HTTP_200_OK
    alerts_data = res_alerts.json()
    assert alerts_data["total"] >= 1

    alert_id = alerts_data["items"][0]["id"]

    # 3. Transition to ACKNOWLEDGED
    res_ack = client.patch(f"/api/v1/alerts/{alert_id}", json={
        "status": "ACKNOWLEDGED",
        "user_name": "Senior CSM Lead"
    })
    assert res_ack.status_code == status.HTTP_200_OK
    ack_data = res_ack.json()
    assert ack_data["status"] == "ACKNOWLEDGED"
    assert ack_data["acknowledged_by"] == "Senior CSM Lead"

    # 4. Transition to RESOLVED
    res_res = client.patch(f"/api/v1/alerts/{alert_id}", json={
        "status": "RESOLVED",
        "user_name": "Senior CSM Lead",
        "resolution_notes": "Llamada realizada al cliente, se ofreció crédito y resolución técnica prioritaria."
    })
    assert res_res.status_code == status.HTTP_200_OK
    res_data = res_res.json()
    assert res_data["status"] == "RESOLVED"
    assert res_data["resolved_by"] == "Senior CSM Lead"
    assert "Llamada realizada" in res_data["resolution_notes"]
