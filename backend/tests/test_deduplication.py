import pytest
from backend.app.services.deduplication import DeduplicationService
from backend.app.schemas.interaction import InteractionCreate
from backend.app.services.ingestion_service import IngestionPipelineService
from backend.app.core.errors import DuplicateInteractionError


def test_hash_generation_and_whitespace_normalization():
    text1 = "  Hola,    tengo un   problema con mi FACTURA  "
    text2 = "hola, tengo un problema con mi factura"

    hash1 = DeduplicationService.generate_hash("CUST-1001", text1)
    hash2 = DeduplicationService.generate_hash("CUST-1001", text2)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex length


def test_duplicate_interaction_is_prevented(db_session):
    """Case 8: Submitting the same interaction twice is stopped by deduplication."""
    payload = InteractionCreate(
        customer_external_id="CUST-TEST-01",
        source_type="support_ticket",
        content="No puedo acceder a mi panel de control desde esta mañana.",
        external_reference_id="TICK-101"
    )

    # First ingestion succeeds
    it1 = IngestionPipelineService.process_single_interaction(db_session, payload)
    assert it1.id is not None
    assert it1.status == "PROCESSED"

    # Second identical ingestion raises DuplicateInteractionError
    with pytest.raises(DuplicateInteractionError):
        IngestionPipelineService.process_single_interaction(db_session, payload)
