from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
    InteractionListResponse
)
from backend.app.services.ingestion_service import IngestionPipelineService
from backend.app.repositories.interaction_repo import InteractionRepository
from backend.app.core.errors import ResourceNotFoundError

router = APIRouter()


@router.post("", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db)
):
    """
    Ingests and processes a new interaction through the full 10-step AI & Risk pipeline.
    Guarantees deduplication, deterministic scoring, and proactive alert triggering.
    """
    interaction = IngestionPipelineService.process_single_interaction(db, payload)
    full_interaction = InteractionRepository.get_by_id(db, interaction.id)
    return full_interaction


@router.get("", response_model=InteractionListResponse)
def list_interactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    customer_id: Optional[int] = Query(None, description="Filter by customer internal ID"),
    status: Optional[str] = Query(None, description="Filter by status (e.g. PROCESSED, PENDING_AI_ANALYSIS)"),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated list of interactions with filters.
    """
    skip = (page - 1) * page_size
    items, total = InteractionRepository.get_list(
        db=db,
        skip=skip,
        limit=page_size,
        customer_id=customer_id,
        status=status
    )
    return InteractionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction_detail(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves full details of a specific interaction including sentiment, frictions, and churn risk.
    """
    interaction = InteractionRepository.get_by_id(db, interaction_id)
    if not interaction:
        raise ResourceNotFoundError(resource_name="Interaction", resource_id=interaction_id)
    return interaction
