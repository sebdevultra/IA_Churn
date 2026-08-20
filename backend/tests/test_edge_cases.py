import pytest
from unittest.mock import patch
from backend.app.schemas.interaction import InteractionCreate
from backend.app.services.ingestion_service import IngestionPipelineService
from backend.app.models.interaction import Interaction
from backend.app.workers.ingestion_worker import IngestionWorker


def test_ai_outage_does_not_lose_interaction(db_session):
    """Case 9: When AI provider fails/crashes, interaction is not lost; remains in PENDING_AI_ANALYSIS."""
    payload = InteractionCreate(
        customer_external_id="CUST-TEST-02",
        source_type="chat",
        content="Mensaje durante caída del proveedor de IA.",
        external_reference_id="CHAT-FAIL-01"
    )

    with patch("backend.app.services.ingestion_service.get_ai_provider") as mock_get_ai:
        mock_provider = mock_get_ai.return_value
        mock_provider.analyze_interaction.side_effect = Exception("503 Service Unavailable / Timeout")

        with pytest.raises(Exception):
            IngestionPipelineService.process_single_interaction(db_session, payload)

        # Query database to confirm interaction was saved and not lost
        saved = db_session.query(Interaction).filter(Interaction.external_reference_id == "CHAT-FAIL-01").first()
        assert saved is not None
        assert saved.status == "PENDING_AI_ANALYSIS"
        assert saved.retry_count == 1
        assert "503" in saved.error_message


def test_retry_pending_interactions_recovers_failed_records(db_session):
    """Case 14: Retrying pending interactions successfully completes them once AI is available."""
    # 1. Create a failed/pending interaction
    customer = IngestionPipelineService.get_or_create_customer(db_session, "CUST-TEST-02")
    it = Interaction(
        customer_id=customer.id,
        source_type="chat",
        content="Excelente atención y rapidez en la respuesta.",
        interaction_hash="test_hash_retry_12345",
        status="PENDING_AI_ANALYSIS",
        retry_count=1,
        error_message="Previous failure"
    )
    db_session.add(it)
    db_session.commit()

    # 2. Run retry mechanism
    reprocessed = IngestionPipelineService.retry_pending_interactions(db_session)
    assert reprocessed >= 1

    db_session.refresh(it)
    assert it.status == "PROCESSED"
    assert it.processed_at is not None
    assert it.sentiment is not None
    assert it.sentiment.sentiment == "positive"


def test_worker_runs_without_exceptions(db_session):
    """Tests IngestionWorker execution job."""
    result = IngestionWorker.run_ingestion_job()
    assert "status" in result or "batch_id" in result
