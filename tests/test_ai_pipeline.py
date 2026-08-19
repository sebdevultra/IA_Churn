"""
Suite Exhaustiva de Pruebas Automatizadas para el Pipeline de IA.
Cubre los 12 Casos de Prueba Obligatorios del Sprint.
"""

import pytest
from datetime import datetime, timezone
from ai_pipeline.schemas import (
    InteractionPayload,
    SentimentType,
    EmotionType,
    FrictionCategory,
    InteractionSource,
)
from ai_pipeline.pipeline import AIPipelineOrchestrator
from ai_pipeline.scheduler_ingestion import AIIngestionWorker


@pytest.fixture
def orchestrator():
    # Inicializado en modo local-first resiliente (sin API key de prueba para determinismo puro)
    return AIPipelineOrchestrator(enable_cloud=False)


# ============================================================================
# 12 CASOS DE PRUEBA OBLIGATORIOS
# ============================================================================

def test_case_01_positive_message(orchestrator):
    """Caso 1: Mensaje positivo directo"""
    payload = InteractionPayload(
        interaction_id="TC-01",
        customer_id="CUST-100",
        source=InteractionSource.REVIEW,
        message="Excelente servicio, la plataforma es muy rápida y el equipo de soporte resolvió mi duda en 5 minutos."
    )
    result = orchestrator.process_interaction(payload)
    assert result.sentiment == SentimentType.POSITIVE
    assert result.emotion == EmotionType.SATISFACTION
    assert result.churn_intent is False
    assert result.confidence >= 0.85


def test_case_02_frustration_and_support_failure(orchestrator):
    """Caso 2: Frustración severa y queja de soporte"""
    payload = InteractionPayload(
        interaction_id="TC-02",
        customer_id="CUST-101",
        source=InteractionSource.SUPPORT_TICKET,
        message="Llevo 3 días con el sistema caído y nadie responde mis mensajes. Es una lentitud y desatención pésima."
    )
    result = orchestrator.process_interaction(payload)
    assert result.sentiment == SentimentType.NEGATIVE
    assert result.emotion in [EmotionType.FRUSTRATION, EmotionType.ANGER]
    assert FrictionCategory.CUSTOMER_SUPPORT in result.friction_points or FrictionCategory.PRODUCT_RELIABILITY in result.friction_points


def test_case_03_explicit_churn_intent(orchestrator):
    """Caso 3: Intención explícita de cancelación / Churn"""
    payload = InteractionPayload(
        interaction_id="TC-03",
        customer_id="CUST-102",
        source=InteractionSource.CHAT,
        message="Estoy harto de los errores constantes. Si no me dan solución hoy, voy a cancelar mi suscripción y pedir el reembolso."
    )
    result = orchestrator.process_interaction(payload)
    assert result.sentiment == SentimentType.NEGATIVE
    assert result.churn_intent is True
    assert result.emotion == EmotionType.ANGER
    assert len(result.evidence) > 0


def test_case_04_ambiguous_sarcasm(orchestrator):
    """Caso 4: Mensaje con sarcasmo e ironía"""
    payload = InteractionPayload(
        interaction_id="TC-04",
        customer_id="CUST-103",
        source=InteractionSource.REVIEW,
        message="Buenísimo el servicio, se cayó el servidor en pleno lanzamiento y me cobraron el doble 👏"
    )
    result = orchestrator.process_interaction(payload)
    assert result.sentiment == SentimentType.NEGATIVE
    assert result.emotion in [EmotionType.FRUSTRATION, EmotionType.ANGER]


def test_case_05_empty_or_noise_message(orchestrator):
    """Caso 5: Mensaje vacío o con solo espacios/puntuación"""
    payload = InteractionPayload(
        interaction_id="TC-05",
        customer_id="CUST-104",
        source=InteractionSource.CHAT,
        message="    ...   "
    )
    result = orchestrator.process_interaction(payload)
    assert result.sentiment == SentimentType.NEUTRAL
    assert result.emotion == EmotionType.NEUTRAL
    assert result.churn_intent is False
    assert result.friction_points == [FrictionCategory.NONE]


def test_case_06_duplicate_interaction_idempotency(orchestrator):
    """Caso 6: Interacción duplicada (Prueba de Idempotencia del Worker)"""
    processed_database = []

    def mock_save(item, res):
        processed_database.append(item.interaction_id)
        return True

    worker = AIIngestionWorker(
        orchestrator=orchestrator,
        save_result_callback=mock_save
    )

    payload1 = InteractionPayload(
        interaction_id="TC-06-DUP",
        customer_id="CUST-105",
        message="Mensaje para probar duplicidad"
    )
    payload2 = InteractionPayload(
        interaction_id="TC-06-DUP",
        customer_id="CUST-105",
        message="Mensaje para probar duplicidad"
    )

    results = worker.process_batch([payload1, payload2])
    assert len(results) == 1  # Solo se procesó una vez
    assert len(processed_database) == 1


def test_case_07_pii_scrubbing_and_sanitization(orchestrator):
    """Caso 7: Mensaje con múltiples datos sensibles (PII & Finanzas)"""
    payload = InteractionPayload(
        interaction_id="TC-07",
        customer_id="CUST-106",
        message="Mi correo es cliente@empresa.com y mi celular es 3109876543. Mi tarjeta es 4532 9988 7766 5544 y me hicieron un cobro no reconocido."
    )
    result = orchestrator.process_interaction(payload)
    assert result.processing_metadata["was_pii_scrubbed"] is True
    assert result.processing_metadata["pii_masked_count"] >= 3
    assert FrictionCategory.BILLING_PRICING in result.friction_points


def test_case_08_cloud_outage_fallback_activation():
    """Caso 8: Caída de la API de Cloud LLM y conmutación transparente a Local NLP"""
    # Orquestador con nube habilitada pero API key inválida para forzar fallback
    orchestrator_fallback = AIPipelineOrchestrator(
        gemini_api_key="INVALID_KEY_FOR_TESTING",
        enable_cloud=True
    )
    payload = InteractionPayload(
        interaction_id="TC-08",
        customer_id="CUST-107",
        message="El sistema no funciona y tengo un cobro duplicado."
    )
    # Debe responder exitosamente sin lanzar excepciones
    result = orchestrator_fallback.process_interaction(payload)
    assert result.sentiment == SentimentType.NEGATIVE
    assert result.confidence > 0.0
    assert result.processing_metadata.get("engine_used") in ["local_nlp", "cloud_gemini"]


def test_case_09_invalid_json_handling_and_validation(orchestrator):
    """Caso 9: Validación estricta de Schemas ante payloads anómalos"""
    payload = InteractionPayload(
        interaction_id="TC-09",
        customer_id="CUST-108",
        message="Texto con caracteres especiales \x00\x08 \n\n\n y formato irregular"
    )
    result = orchestrator.process_interaction(payload)
    assert isinstance(result.sentiment, SentimentType)
    assert isinstance(result.confidence, float)
    assert 0.0 <= result.confidence <= 1.0


def test_case_10_multiple_messages_same_customer(orchestrator):
    """Caso 10: Múltiples mensajes del mismo cliente preservando metadata"""
    payload1 = InteractionPayload(
        interaction_id="TC-10-A",
        customer_id="CUST-VIP-1",
        customer_history_count=0,
        customer_tier="Enterprise",
        message="Reporto primera lentitud en el servidor."
    )
    payload2 = InteractionPayload(
        interaction_id="TC-10-B",
        customer_id="CUST-VIP-1",
        customer_history_count=2,  # Cliente recurrente
        customer_tier="Enterprise",
        message="Sigue la lentitud. Si no lo solucionan buscaremos otro proveedor."
    )

    res1 = orchestrator.process_interaction(payload1)
    res2 = orchestrator.process_interaction(payload2)

    assert res2.churn_intent is True
    assert res2.processing_metadata["customer_id"] == "CUST-VIP-1"


def test_case_11_long_text_history(orchestrator):
    """Caso 11: Texto muy extenso (+2000 caracteres) sin desbordamiento ni fallos"""
    long_text = "El servicio ha tenido varios inconvenientes. " * 50 + " Finalmente cancelo el servicio."
    payload = InteractionPayload(
        interaction_id="TC-11",
        customer_id="CUST-109",
        message=long_text
    )
    result = orchestrator.process_interaction(payload)
    assert result.churn_intent is True
    assert len(result.evidence) > 0


def test_case_12_failure_recovery_in_scheduler(orchestrator):
    """Caso 12: Recuperación tras fallo en lote de ingesta"""
    failed_attempts = []
    success_saves = []

    def mock_fetch():
        return [
            InteractionPayload(interaction_id="TC-12-OK1", customer_id="C-1", message="Todo bien"),
            InteractionPayload(interaction_id="TC-12-FAIL", customer_id="C-2", message="Error simulado"),
            InteractionPayload(interaction_id="TC-12-OK2", customer_id="C-3", message="Excelente"),
        ]

    def mock_save(item, res):
        if item.interaction_id == "TC-12-FAIL":
            return False  # Simula fallo en base de datos
        success_saves.append(item.interaction_id)
        return True

    def mock_mark_error(i_id, err):
        failed_attempts.append(i_id)

    worker = AIIngestionWorker(
        orchestrator=orchestrator,
        fetch_pending_callback=mock_fetch,
        save_result_callback=mock_save,
        mark_error_callback=mock_mark_error
    )

    processed_count = worker.run_tick()
    # 2 de 3 se procesaron exitosamente, 1 se marcó para retry sin romper el scheduler
    assert processed_count == 2
    assert "TC-12-OK1" in success_saves
    assert "TC-12-OK2" in success_saves
    assert "TC-12-FAIL" in failed_attempts
