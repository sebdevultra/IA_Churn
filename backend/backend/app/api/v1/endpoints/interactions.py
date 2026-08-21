import io
import csv
import time
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status, UploadFile, File
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
    InteractionListResponse
)
from backend.app.services.ingestion_service import IngestionPipelineService
from backend.app.repositories.interaction_repo import InteractionRepository
from backend.app.core.errors import ResourceNotFoundError, InvalidContentFormatError, DuplicateInteractionError

router = APIRouter()


from backend.app.models.alert import Alert

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db)
):
    """
    Ingests and processes a new interaction through the full 10-step AI & Risk pipeline.
    Guarantees deduplication, deterministic scoring, and proactive alert triggering.
    Returns unified response compatible with Horizon UI and REST clients.
    """
    interaction = IngestionPipelineService.process_single_interaction(db, payload)
    full_interaction = InteractionRepository.get_by_id(db, interaction.id)

    cust = full_interaction.customer
    sentiment = full_interaction.sentiment
    churn = full_interaction.churn_risk
    alert = db.query(Alert).filter(Alert.churn_risk_id == (churn.id if churn else -1)).first()

    factors = []
    if churn and churn.score_breakdown:
        sb = churn.score_breakdown
        if isinstance(sb, list):
            for item in sb:
                if isinstance(item, dict):
                    factor_name = item.get("reason") or item.get("factor") or item.get("rule_name", "Factor de Riesgo").replace("_", " ").title()
                    impact_val = int(item.get("impact", item.get("weight", 10)))
                    factors.append({"factor": factor_name, "impact": impact_val})
    if not factors and churn:
        factors = [
            {"factor": f"Riesgo {churn.risk_level}", "impact": int(churn.risk_score * 0.4)},
            {"factor": f"Tier {cust.tier if cust else 'Standard'}", "impact": 20 if (cust and cust.tier == 'Enterprise') else 10}
        ]

    friction_str = full_interaction.frictions[0].category if full_interaction.frictions else "customer_support"
    raw_content = full_interaction.content

    masked_content = raw_content
    if sentiment and sentiment.evidence and len(sentiment.evidence) > 0:
        masked_content = sentiment.evidence[0]

    if alert:
        if alert.status in ["NEW", "PENDING"]:
            status_str = "PENDING"
        elif alert.status in ["ACKNOWLEDGED", "IN_REVIEW"]:
            status_str = "IN_REVIEW"
        else:
            status_str = alert.status
    else:
        status_str = "PENDING" if (churn and churn.risk_score >= 60) else "RESOLVED"

    case_data = {
        "id": f"ALT-{alert.id}" if alert else f"INT-{full_interaction.id}",
        "db_alert_id": alert.id if alert else None,
        "customerName": cust.name if cust else "Cliente",
        "tier": cust.tier if cust else "Standard",
        "riskScore": churn.risk_score if churn else 10,
        "emotion": sentiment.emotion if sentiment else "neutral",
        "friction": friction_str,
        "rawEvidence": raw_content,
        "maskedEvidence": masked_content,
        "status": status_str,
        "aiEngine": sentiment.model_name if sentiment else "local_nlp",
        "scoreFactors": factors,
        "timestamp": full_interaction.created_at.isoformat()
    }

    return {
        "success": True,
        "data": case_data,
        "interaction_id": full_interaction.id,
        "status": full_interaction.status
    }


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


@router.post("/upload-csv", response_model=dict, status_code=status.HTTP_200_OK)
def upload_interactions_csv(
    file: UploadFile = File(...),
    max_records: Optional[int] = Query(None, description="Límite opcional de registros a procesar"),
    db: Session = Depends(get_db)
):
    """
    Recibe y procesa un archivo .CSV limpio de interacciones a través del AI Pipeline completo en modo batch.
    Ejecuta en thread pool con alto throughput (sub-segundo para 1,000 registros).
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise InvalidContentFormatError("El archivo seleccionado debe ser un archivo válido con extensión .csv")

    content_bytes = file.file.read()
    text_stream = io.StringIO(content_bytes.decode("utf-8", errors="ignore"))
    reader = csv.DictReader(text_stream)

    batch_id = f"upload-csv-{uuid.uuid4().hex[:8]}"
    payloads = []

    for row in reader:
        if max_records and len(payloads) >= max_records:
            break

        cust_id = row.get("customer_external_id") or row.get("Cliente_ID") or row.get("customer_id") or "CUST-UNKNOWN"
        channel = row.get("source_type") or row.get("Canal") or "support_ticket"
        tier = row.get("tier") or row.get("Tier") or "Standard"
        content = row.get("content") or row.get("Mensaje_Cliente") or ""
        ref_id = row.get("external_reference_id") or row.get("ID") or f"CSV-{uuid.uuid4().hex[:8]}"

        if not content.strip():
            continue

        try:
            payload = InteractionCreate(
                customer_external_id=cust_id,
                customerName=f"Cliente {cust_id}" if "CUST" in cust_id else cust_id,
                tier=tier,
                source_type=channel,
                content=content,
                external_reference_id=ref_id
            )
            payloads.append(payload)
        except Exception:
            pass

    res = IngestionPipelineService.process_batch_interactions(db, payloads, batch_id=batch_id)
    res["filename"] = file.filename
    return res
