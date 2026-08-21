import pytest
from fastapi import status


def test_list_and_create_customer(client):
    """Tests GET /customers and POST /customers."""
    # List customers
    res = client.get("/api/v1/customers")
    assert res.status_code == status.HTTP_200_OK
    cust_list = res.json()
    assert len(cust_list) >= 2

    # Create new customer
    new_cust = {
        "external_id": "CUST-NEW-99",
        "name": "New Logistics Corp",
        "email": "ops@newlogistics.com",
        "tier": "enterprise",
        "historical_summary": "Cliente nuevo"
    }
    res_create = client.post("/api/v1/customers", json=new_cust)
    assert res_create.status_code == status.HTTP_201_CREATED
    data = res_create.json()
    assert data["external_id"] == "CUST-NEW-99"

    # Fetch Customer Detail
    cust_id = data["id"]
    res_detail = client.get(f"/api/v1/customers/{cust_id}")
    assert res_detail.status_code == status.HTTP_200_OK
    detail_data = res_detail.json()
    assert detail_data["name"] == "New Logistics Corp"

    # Update Customer
    res_patch = client.patch(f"/api/v1/customers/{cust_id}", json={"name": "New Logistics Global Corp"})
    assert res_patch.status_code == status.HTTP_200_OK
    assert res_patch.json()["name"] == "New Logistics Global Corp"


def test_customer_not_found_returns_404(client):
    res = client.get("/api/v1/customers/999999")
    assert res.status_code == status.HTTP_404_NOT_FOUND
