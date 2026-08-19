"""
Pruebas Unitarias para el Módulo de Limpieza y PII Scrubber (ai_pipeline/cleaner.py)
"""

import pytest
from ai_pipeline.cleaner import TextCleanerAndPIIScrubber
from ai_pipeline.schemas import (
    InteractionPayload,
    AISemanticAnalysisResult,
    SentimentType,
    EmotionType,
    FrictionCategory,
    InteractionSource,
)


@pytest.fixture
def scrubber():
    return TextCleanerAndPIIScrubber()


def test_cleaner_empty_and_whitespace(scrubber):
    res = scrubber.scrub_pii("   ")
    assert res.cleaned_text == ""
    assert res.total_pii_masked == 0
    assert not res.was_modified


def test_cleaner_scrub_email_and_phone(scrubber):
    text = "Mi correo es juan.perez@empresa.com y mi celular es +57 300 123 4567 por favor llamar."
    res = scrubber.scrub_pii(text)
    assert "[EMAIL_MASKED]" in res.cleaned_text
    assert "[PHONE_MASKED]" in res.cleaned_text
    assert "juan.perez@empresa.com" not in res.cleaned_text
    assert "300 123 4567" not in res.cleaned_text
    assert res.pii_breakdown.get("emails") == 1
    assert res.pii_breakdown.get("phones") == 1
    assert res.total_pii_masked >= 2


def test_cleaner_scrub_credit_card_and_cvc(scrubber):
    text = "Hice el pago con la tarjeta 4532 8901 2345 6789 y el CVC: 789 pero me cobraron dos veces."
    res = scrubber.scrub_pii(text)
    assert "[CARD_NUMBER_MASKED]" in res.cleaned_text
    assert "[CVC_MASKED]" in res.cleaned_text
    assert "4532 8901 2345 6789" not in res.cleaned_text
    assert "789" not in res.cleaned_text


def test_cleaner_scrub_id_doc_and_bank_account(scrubber):
    text = "Soy cliente con Cédula 1020304050 y mi cuenta de ahorros No. 9876543210 presenta inconsistencias."
    res = scrubber.scrub_pii(text)
    assert "[ID_DOC_MASKED]" in res.cleaned_text
    assert "[BANK_ACCOUNT_MASKED]" in res.cleaned_text
    assert "1020304050" not in res.cleaned_text
    assert "9876543210" not in res.cleaned_text


def test_cleaner_scrub_ip_and_secrets(scrubber):
    text = "El error viene de la IP 192.168.1.100 usando la api_key=sk_live_998877665544 para autenticar."
    res = scrubber.scrub_pii(text)
    assert "[IP_MASKED]" in res.cleaned_text
    assert "[SECRET_MASKED]" in res.cleaned_text
    assert "192.168.1.100" not in res.cleaned_text
    assert "sk_live_998877665544" not in res.cleaned_text


def test_cleaner_scrub_direct_names_and_address(scrubber):
    text = "Mi nombre es Carlos Gómez y vivo en Carrera 45 # 12-34 en Bogotá."
    res = scrubber.scrub_pii(text)
    assert "[NAME_MASKED]" in res.cleaned_text
    assert "[ADDRESS_MASKED]" in res.cleaned_text
    assert "Carlos Gómez" not in res.cleaned_text


def test_schemas_validation():
    payload = InteractionPayload(
        interaction_id="INT-1001",
        customer_id="CUST-500",
        source=InteractionSource.SUPPORT_TICKET,
        message="  Excelente servicio técnico  ",
        customer_history_count=1,
        customer_tier="Enterprise"
    )
    assert payload.message == "Excelente servicio técnico"
    assert payload.customer_tier == "Enterprise"

    result = AISemanticAnalysisResult(
        sentiment=SentimentType.POSITIVE,
        emotion=EmotionType.SATISFACTION,
        friction_points=[FrictionCategory.NONE],
        churn_intent=False,
        confidence=0.95,
        evidence=["Excelente servicio técnico"],
        processing_metadata={"engine_used": "local_nlp"}
    )
    assert result.sentiment == SentimentType.POSITIVE
    assert result.confidence == 0.95
    assert result.friction_points == [FrictionCategory.NONE]
