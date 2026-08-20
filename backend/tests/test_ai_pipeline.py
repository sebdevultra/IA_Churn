import pytest
from backend.app.schemas.ai_response import AIAnalysisOutput, AIContextInput, FrictionItem
from backend.app.services.ai_service import DeterministicRuleAIProvider, OpenAILLMProvider
from backend.app.core.errors import AIProcessingError


def test_deterministic_ai_provider_positive_analysis():
    provider = DeterministicRuleAIProvider()
    context = AIContextInput(customer_id="CUST-101", historical_summary="")

    output, p_tok, c_tok, model = provider.analyze_interaction(
        content="Excelente servicio, estoy muy satisfecho con la atención brindada.",
        context=context
    )

    assert output.sentiment == "positive"
    assert output.churn_intent is False
    assert output.confidence >= 0.90
    assert len(output.evidence) > 0


def test_deterministic_ai_provider_frustration_and_support_frictions():
    provider = DeterministicRuleAIProvider()
    context = AIContextInput(customer_id="CUST-101", historical_summary="")

    output, p_tok, c_tok, model = provider.analyze_interaction(
        content="Estoy harto de esperar días para recibir soporte técnico. Esto es inaceptable.",
        context=context
    )

    assert output.sentiment == "negative"
    assert output.emotion in ["frustration", "anger"]
    assert any(f.category == "customer_support" for f in output.friction_points)


def test_deterministic_ai_provider_explicit_cancellation():
    provider = DeterministicRuleAIProvider()
    context = AIContextInput(customer_id="CUST-101", historical_summary="")

    output, p_tok, c_tok, model = provider.analyze_interaction(
        content="Si no arreglan este error voy a cancelar mi suscripción anual de inmediato.",
        context=context
    )

    assert output.churn_intent is True
    assert output.sentiment == "negative"


def test_json_sanitizer_and_repair_with_markdown_fences():
    provider = OpenAILLMProvider()
    raw_markdown = """```json
    {
      "sentiment": "negative",
      "emotion": "frustration",
      "friction_points": [
        {"category": "billing", "description": "Cobro duplicado", "severity": "high"}
      ],
      "churn_intent": true,
      "confidence": 0.95,
      "evidence": ["Cobro duplicado"]
    }
    ```"""

    parsed = provider._sanitize_and_repair_json(raw_markdown)
    assert parsed["sentiment"] == "negative"
    assert parsed["churn_intent"] is True

    validated = AIAnalysisOutput.model_validate(parsed)
    assert validated.sentiment == "negative"
    assert validated.friction_points[0].category == "billing"


def test_pydantic_schema_rejects_invalid_structure():
    with pytest.raises(Exception):
        # Missing required sentiment and confidence
        AIAnalysisOutput.model_validate({"emotion": "frustration"})
