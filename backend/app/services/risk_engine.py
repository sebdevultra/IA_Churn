from typing import List, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.app.core.risk_rules import (
    RiskWeightsConfig,
    RiskLevel,
    ScoreFactor,
    RiskCalculationResult,
    get_risk_level_from_score
)
from backend.app.models.customer import Customer
from backend.app.models.interaction import Interaction
from backend.app.models.sentiment import SentimentAnalysis
from backend.app.models.friction import FrictionPoint
from backend.app.schemas.ai_response import AIAnalysisOutput
from backend.app.core.logging import logger


class RiskEngine:
    """
    Deterministic Churn Risk Engine.
    All mathematical score calculations are strictly executed in Python without LLM hallucination.
    """

    @classmethod
    def calculate_risk(
        cls,
        db: Session,
        customer: Customer,
        ai_output: AIAnalysisOutput
    ) -> RiskCalculationResult:
        factors: List[ScoreFactor] = []
        raw_score = 0
        summary_reasons: List[str] = []

        # 1. Sentiment Score Factor
        sentiment_weight = 0
        if ai_output.sentiment == "negative":
            sentiment_weight = RiskWeightsConfig.SENTIMENT_NEGATIVE
            factors.append(ScoreFactor(
                rule_name="SENTIMENT_NEGATIVE",
                weight=sentiment_weight,
                applied=True,
                reason="Sentimiento negativo detectado en la interacción"
            ))
            summary_reasons.append("Sentimiento negativo")
        elif ai_output.sentiment == "positive":
            sentiment_weight = RiskWeightsConfig.SENTIMENT_POSITIVE
            factors.append(ScoreFactor(
                rule_name="SENTIMENT_POSITIVE",
                weight=sentiment_weight,
                applied=True,
                reason="Sentimiento positivo (reduce riesgo acumulado)"
            ))
        else:
            factors.append(ScoreFactor(
                rule_name="SENTIMENT_NEUTRAL",
                weight=RiskWeightsConfig.SENTIMENT_NEUTRAL,
                applied=False,
                reason="Sentimiento neutral"
            ))
        raw_score += sentiment_weight

        # 2. Emotion Score Factor
        emotion_weight = 0
        if ai_output.emotion == "anger":
            emotion_weight = RiskWeightsConfig.EMOTION_ANGER
            factors.append(ScoreFactor(
                rule_name="EMOTION_ANGER",
                weight=emotion_weight,
                applied=True,
                reason="Emoción de enojo/ira detectada"
            ))
            summary_reasons.append("Enojo/Ira del cliente")
        elif ai_output.emotion == "frustration":
            emotion_weight = RiskWeightsConfig.EMOTION_FRUSTRATION
            factors.append(ScoreFactor(
                rule_name="EMOTION_FRUSTRATION",
                weight=emotion_weight,
                applied=True,
                reason="Emoción de frustración detectada"
            ))
            summary_reasons.append("Frustración del cliente")
        elif ai_output.emotion == "disappointment":
            emotion_weight = RiskWeightsConfig.EMOTION_DISAPPOINTMENT
            factors.append(ScoreFactor(
                rule_name="EMOTION_DISAPPOINTMENT",
                weight=emotion_weight,
                applied=True,
                reason="Emoción de decepción detectada"
            ))
            summary_reasons.append("Decepción manifestada")
        elif ai_output.emotion == "joy":
            emotion_weight = RiskWeightsConfig.EMOTION_JOY
            factors.append(ScoreFactor(
                rule_name="EMOTION_JOY",
                weight=emotion_weight,
                applied=True,
                reason="Emoción de alegría/entusiasmo (reduce riesgo)"
            ))
        elif ai_output.emotion == "satisfaction":
            emotion_weight = RiskWeightsConfig.EMOTION_SATISFACTION
            factors.append(ScoreFactor(
                rule_name="EMOTION_SATISFACTION",
                weight=emotion_weight,
                applied=True,
                reason="Emoción de satisfacción (reduce riesgo)"
            ))
        raw_score += emotion_weight

        # 3. Explicit Churn Intent
        if ai_output.churn_intent:
            churn_weight = RiskWeightsConfig.CHURN_INTENT_EXPLICIT
            factors.append(ScoreFactor(
                rule_name="CHURN_INTENT_EXPLICIT",
                weight=churn_weight,
                applied=True,
                reason="Intención explícita de cancelar o migrar de servicio"
            ))
            summary_reasons.append("Intención explícita de cancelar")
            raw_score += churn_weight

        # 4. Specific Friction Points (e.g. Customer Support)
        has_support_friction = any(f.category == "customer_support" for f in ai_output.friction_points)
        if has_support_friction:
            support_weight = RiskWeightsConfig.FRICTION_SUPPORT_ISSUE
            factors.append(ScoreFactor(
                rule_name="FRICTION_SUPPORT_ISSUE",
                weight=support_weight,
                applied=True,
                reason="Puntos de fricción con servicio/soporte al cliente"
            ))
            summary_reasons.append("Mala experiencia con soporte")
            raw_score += support_weight

        # 5. Recurrent Friction Analysis (Historical Check)
        past_interactions = (
            db.query(Interaction)
            .filter(
                Interaction.customer_id == customer.id,
                Interaction.status == "PROCESSED"
            )
            .order_by(Interaction.created_at.desc())
            .limit(3)
            .all()
        )

        if past_interactions and ai_output.friction_points:
            past_ids = [it.id for it in past_interactions]
            past_friction_categories: Set[str] = {
                f[0] for f in db.query(FrictionPoint.category).filter(FrictionPoint.interaction_id.in_(past_ids)).all()
            }
            current_categories = {f.category for f in ai_output.friction_points}
            common_frictions = past_friction_categories.intersection(current_categories)

            if common_frictions:
                recurrent_weight = RiskWeightsConfig.RECURRENT_FRICTION_ISSUE
                factors.append(ScoreFactor(
                    rule_name="RECURRENT_FRICTION_ISSUE",
                    weight=recurrent_weight,
                    applied=True,
                    reason=f"Fricción recurrente detectada en categorías: {', '.join(common_frictions)}"
                ))
                summary_reasons.append(f"Fricción recurrente ({', '.join(common_frictions)})")
                raw_score += recurrent_weight

        # 6. Recent Negative Signal Check (Within last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_negative = (
            db.query(SentimentAnalysis)
            .join(Interaction, SentimentAnalysis.interaction_id == Interaction.id)
            .filter(
                Interaction.customer_id == customer.id,
                Interaction.created_at >= seven_days_ago,
                SentimentAnalysis.sentiment == "negative"
            )
            .first()
        )
        if recent_negative and ai_output.sentiment == "negative":
            recent_weight = RiskWeightsConfig.RECENT_NEGATIVE_SIGNAL
            factors.append(ScoreFactor(
                rule_name="RECENT_NEGATIVE_SIGNAL",
                weight=recent_weight,
                applied=True,
                reason="Señales negativas acumuladas en los últimos 7 días"
            ))
            summary_reasons.append("Señales negativas recientes acumuladas")
            raw_score += recent_weight

        # 7. Enterprise Tier Multiplier
        if customer.tier and customer.tier.lower() == "enterprise" and raw_score > 0:
            multiplier = RiskWeightsConfig.TIER_ENTERPRISE_MULTIPLIER
            adjusted_score = int(round(raw_score * multiplier))
            diff = adjusted_score - raw_score
            if diff > 0:
                factors.append(ScoreFactor(
                    rule_name="TIER_ENTERPRISE_MULTIPLIER",
                    weight=diff,
                    applied=True,
                    reason=f"Factor multiplicador 1.1x por cuenta Enterprise de alto valor"
                ))
                raw_score = adjusted_score

        # 8. Confidence Dampening
        if ai_output.confidence < RiskWeightsConfig.MIN_CONFIDENCE_THRESHOLD:
            dampener = 0.8
            dampened_score = int(round(raw_score * dampener))
            diff = dampened_score - raw_score
            factors.append(ScoreFactor(
                rule_name="LOW_CONFIDENCE_DAMPENER",
                weight=diff,
                applied=True,
                reason=f"Ajuste por confianza baja del modelo ({ai_output.confidence:.2f})"
            ))
            raw_score = dampened_score

        # 9. Clamp Final Score to [0, 100]
        final_score = max(RiskWeightsConfig.MIN_SCORE, min(raw_score, RiskWeightsConfig.MAX_SCORE))
        risk_level = get_risk_level_from_score(final_score)
        is_critical = (risk_level == RiskLevel.CRITICAL)

        logger.info(
            f"Risk calculated for Customer {customer.external_id}: Raw={raw_score}, Final={final_score}, Level={risk_level.value}"
        )

        return RiskCalculationResult(
            raw_score=raw_score,
            final_score=final_score,
            risk_level=risk_level,
            breakdown=factors,
            summary_reasons=summary_reasons if summary_reasons else ["Sin factores de riesgo críticos identificados"],
            is_critical=is_critical
        )
