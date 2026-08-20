from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.customer import (
    CustomerResponse,
    CustomerDetailResponse,
    CustomerCreate,
    CustomerUpdate
)
from backend.app.repositories.customer_repo import CustomerRepository
from backend.app.models.alert import Alert
from backend.app.models.interaction import Interaction
from backend.app.core.errors import ResourceNotFoundError

router = APIRouter()


@router.get("", response_model=List[CustomerResponse])
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    risk_level: Optional[str] = Query(None, description="Filter by risk level: LOW, MEDIUM, HIGH, CRITICAL"),
    db: Session = Depends(get_db)
):
    """
    Retrieves customers sorted by highest churn risk score.
    """
    skip = (page - 1) * page_size
    items, _ = CustomerRepository.get_list(db, skip=skip, limit=page_size, risk_level=risk_level)
    return items


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer_profile(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves comprehensive customer profile with historical summary, open alerts, and interactions count.
    """
    customer = CustomerRepository.get_by_id(db, customer_id)
    if not customer:
        raise ResourceNotFoundError(resource_name="Customer", resource_id=customer_id)

    recent_interactions_count = db.query(Interaction).filter(Interaction.customer_id == customer.id).count()
    open_alerts_count = db.query(Alert).filter(Alert.customer_id == customer.id, Alert.status.in_(["NEW", "ACKNOWLEDGED"])).count()

    return CustomerDetailResponse(
        id=customer.id,
        external_id=customer.external_id,
        name=customer.name,
        email=customer.email,
        tier=customer.tier,
        historical_summary=customer.historical_summary,
        current_risk_score=customer.current_risk_score,
        current_risk_level=customer.current_risk_level,
        last_interaction_at=customer.last_interaction_at,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        recent_interactions_count=recent_interactions_count,
        open_alerts_count=open_alerts_count
    )


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Registers a new customer manually.
    """
    return CustomerRepository.create(db, payload)


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates customer details.
    """
    customer = CustomerRepository.get_by_id(db, customer_id)
    if not customer:
        raise ResourceNotFoundError(resource_name="Customer", resource_id=customer_id)
    return CustomerRepository.update(db, customer, payload)
