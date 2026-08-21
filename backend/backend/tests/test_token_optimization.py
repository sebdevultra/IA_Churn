import pytest
from backend.app.models.customer import Customer
from backend.app.schemas.ai_response import AIAnalysisOutput, FrictionItem
from backend.app.services.context_manager import ContextManagerService


def test_compact_context_construction(db_session):
    """Case 11: Long history customer produces a compact, token-efficient context input."""
    customer = db_session.query(Customer).filter(Customer.external_id == "CUST-TEST-01").first()
    customer.historical_summary = "Cliente corporativo con 5 incidencias técnicas previas."
    db_session.commit()

    context = ContextManagerService.build_compact_context(db_session, customer)

    assert context.customer_id == "CUST-TEST-01"
    assert context.tier == "enterprise"
    assert "Cliente corporativo" in context.historical_summary
    # Context payload representation remains minimal
    json_rep = context.model_dump_json()
    assert len(json_rep.split()) < 60  # Under 60 words (< 100 tokens)


def test_incremental_summary_update_bounds_memory(db_session):
    """Verifies that updating customer summary keeps bounded size to avoid unbounded token growth."""
    customer = db_session.query(Customer).filter(Customer.external_id == "CUST-TEST-02").first()
    customer.historical_summary = "Nota antigua 1 | Nota antigua 2 | Nota antigua 3"

    ai_output = AIAnalysisOutput(
        sentiment="negative",
        emotion="frustration",
        friction_points=[FrictionItem(category="billing", description="Error en cobro")],
        churn_intent=True,
        confidence=0.95,
        evidence=["Cobro indebido"]
    )

    ContextManagerService.update_customer_summary(
        db=db_session,
        customer=customer,
        new_analysis=ai_output,
        content="Cobro indebido en factura"
    )

    # Historical summary must retain at most last 2 notes + new note
    parts = customer.historical_summary.split(" | ")
    assert len(parts) <= 2
    assert "CRÍTICO" in customer.historical_summary
