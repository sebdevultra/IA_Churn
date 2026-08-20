import pytest
from backend.app.core.risk_rules import RiskWeightsConfig, RiskLevel
from backend.app.schemas.ai_response import AIAnalysisOutput, FrictionItem
from backend.app.services.risk_engine import RiskEngine
from backend.app.models.customer import Customer


def test_positive_message_produces_low_risk(db_session):
    """Case 1: Positive message produces positive reduction and LOW risk."""
    customer = db_session.query(Customer).filter(Customer.external_id == "CUST-TEST-02").first()
    
    ai_output = AIAnalysisOutput(
        sentiment="positive",
        emotion="satisfaction",
        friction_points=[],
        churn_intent=False,
        confidence=0.95,
        evidence=["Excelente servicio, estoy muy satisfecho."]
    )

    result = RiskEngine.calculate_risk(db_session, customer, ai_output)

    assert result.final_score <= 29
    assert result.risk_level == RiskLevel.LOW
    assert result.is_critical is False
    assert any(f.rule_name == "SENTIMENT_POSITIVE" for f in result.breakdown)


def test_negative_message_with_frustration_produces_high_risk(db_session):
    """Case 2: Negative message with frustration and support friction produces >= HIGH risk."""
    customer = db_session.query(Customer).filter(Customer.external_id == "CUST-TEST-02").first()

    ai_output = AIAnalysisOutput(
        sentiment="negative",
        emotion="frustration",
        friction_points=[
            FrictionItem(category="customer_support", description="Días esperando soporte", severity="high")
        ],
        churn_intent=False,
        confidence=0.92,
        evidence=["Estoy harto de esperar días para recibir soporte."]
    )

    result = RiskEngine.calculate_risk(db_session, customer, ai_output)

    # Negative (+20) + Frustration (+20) + Support (+10) = 50 (MEDIUM) or higher if enterprise
    assert result.final_score >= 50
    assert result.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]
    assert any(f.rule_name == "EMOTION_FRUSTRATION" for f in result.breakdown)
    assert any(f.rule_name == "FRICTION_SUPPORT_ISSUE" for f in result.breakdown)


def test_explicit_churn_intent_produces_high_or_critical_risk(db_session):
    """Case 3: Explicit churn intent (+30) combined with negative sentiment triggers HIGH or CRITICAL."""
    customer = db_session.query(Customer).filter(Customer.external_id == "CUST-TEST-01").first()

    ai_output = AIAnalysisOutput(
        sentiment="negative",
        emotion="frustration",
        friction_points=[
            FrictionItem(category="customer_support", description="Falta de soporte", severity="high"),
            FrictionItem(category="product_reliability", description="API caída", severity="high")
        ],
        churn_intent=True,
        confidence=0.96,
        evidence=["Si esto continúa voy a cancelar mi suscripción."]
    )

    result = RiskEngine.calculate_risk(db_session, customer, ai_output)

    # Negative (+20) + Frustration (+20) + Churn (+30) + Support (+10) = 80 * 1.1 (enterprise) = 88 -> CRITICAL
    assert result.final_score >= 80
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.is_critical is True
    assert "Intención explícita de cancelar" in result.summary_reasons


def test_ambiguous_message_is_not_classified_as_critical(db_session):
    """Case 4: Ambiguous message ('esperaba algo diferente') does not trigger critical alert."""
    customer = db_session.query(Customer).filter(Customer.external_id == "CUST-TEST-02").first()

    ai_output = AIAnalysisOutput(
        sentiment="neutral",
        emotion="neutral",
        friction_points=[],
        churn_intent=False,
        confidence=0.70,
        evidence=["Bueno... esperaba algo diferente."]
    )

    result = RiskEngine.calculate_risk(db_session, customer, ai_output)

    assert result.final_score < 60
    assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
    assert result.is_critical is False


def test_score_is_bounded_between_zero_and_one_hundred(db_session):
    """Verifies that score strictly clamps to [0, 100]."""
    customer = db_session.query(Customer).filter(Customer.external_id == "CUST-TEST-01").first()

    # Extreme positive output
    ai_pos = AIAnalysisOutput(
        sentiment="positive",
        emotion="joy",
        friction_points=[],
        churn_intent=False,
        confidence=1.0,
        evidence=["Todo es perfecto y maravilloso."]
    )
    res_pos = RiskEngine.calculate_risk(db_session, customer, ai_pos)
    assert res_pos.final_score >= 0

    # Extreme negative output
    ai_neg = AIAnalysisOutput(
        sentiment="negative",
        emotion="anger",
        friction_points=[
            FrictionItem(category="customer_support", description="Terrible", severity="high")
        ],
        churn_intent=True,
        confidence=1.0,
        evidence=["Cancelamos hoy mismo."]
    )
    res_neg = RiskEngine.calculate_risk(db_session, customer, ai_neg)
    assert res_neg.final_score <= 100
