"""
Pruebas Unitarias para el Motor Local NLP (ai_pipeline/local_nlp_fallback.py)
"""

import pytest
from ai_pipeline.local_nlp_fallback import LocalNLPSentimentEngine
from ai_pipeline.schemas import SentimentType, EmotionType, FrictionCategory


@pytest.fixture
def nlp_engine():
    return LocalNLPSentimentEngine()


def test_positive_message(nlp_engine):
    text = "Excelente servicio, la plataforma es muy rápida y el soporte solucionó todo en minutos. ¡Muchas gracias!"
    result = nlp_engine.analyze(text)
    assert result.sentiment == SentimentType.POSITIVE
    assert result.emotion == EmotionType.SATISFACTION
    assert not result.churn_intent
    assert result.confidence >= 0.85
    assert result.processing_metadata["latency_ms"] < 50.0  # Latencia ultrarrápida


def test_frustration_and_support_delay(nlp_engine):
    text = "Llevo 3 días con el sistema caído y nadie responde mis tickets de soporte. Es una demora inaceptable."
    result = nlp_engine.analyze(text)
    assert result.sentiment == SentimentType.NEGATIVE
    assert result.emotion in [EmotionType.FRUSTRATION, EmotionType.ANGER]
    assert FrictionCategory.CUSTOMER_SUPPORT in result.friction_points or FrictionCategory.PRODUCT_RELIABILITY in result.friction_points
    assert not result.churn_intent


def test_explicit_churn_intent(nlp_engine):
    text = "El servicio es pésimo y las fallas son constantes. Si no lo arreglan hoy, voy a cancelar mi suscripción anual."
    result = nlp_engine.analyze(text)
    assert result.sentiment == SentimentType.NEGATIVE
    assert result.churn_intent is True
    assert result.emotion == EmotionType.ANGER


def test_billing_and_pricing_friction(nlp_engine):
    text = "Me llegó un cobro no reconocido en la factura y el aumento de precio no fue avisado."
    result = nlp_engine.analyze(text)
    assert FrictionCategory.BILLING_PRICING in result.friction_points


def test_sarcasm_detection(nlp_engine):
    text = "Buenísimo el servicio, se cayó la base de datos en pleno lanzamiento y me cobraron el doble 👏"
    result = nlp_engine.analyze(text)
    assert result.sentiment == SentimentType.NEGATIVE
    assert result.emotion in [EmotionType.FRUSTRATION, EmotionType.ANGER]
    assert result.processing_metadata.get("is_sarcastic") is True


def test_empty_and_noise_text(nlp_engine):
    result = nlp_engine.analyze("")
    assert result.sentiment == SentimentType.NEUTRAL
    assert result.emotion == EmotionType.NEUTRAL
    assert result.friction_points == [FrictionCategory.NONE]
    assert not result.churn_intent


def test_negation_inversion(nlp_engine):
    text = "El producto no es bueno y el equipo nunca respondió."
    result = nlp_engine.analyze(text)
    assert result.sentiment == SentimentType.NEGATIVE
    assert result.emotion in [EmotionType.FRUSTRATION, EmotionType.ANGER]
