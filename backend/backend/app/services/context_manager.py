from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.customer import Customer
from backend.app.models.interaction import Interaction
from backend.app.models.sentiment import SentimentAnalysis
from backend.app.models.friction import FrictionPoint
from backend.app.models.churn_risk import ChurnRisk
from backend.app.schemas.ai_response import AIContextInput, AIAnalysisOutput
from backend.app.core.logging import logger


class ContextManagerService:
    """
    Context Management & Token Optimization Engine.
    Prevents token explosion by aggregating sliding-window indicators and compact summaries
    instead of sending raw interaction histories.
    """

    @classmethod
    def build_compact_context(cls, db: Session, customer: Customer) -> AIContextInput:
        """
        Builds a lightweight structured context payload (< 150 tokens) for LLM analysis.
        """
        # Fetch last 3 past interactions for this customer
        last_interactions = (
            db.query(Interaction)
            .filter(
                Interaction.customer_id == customer.id,
                Interaction.status == "PROCESSED"
            )
            .order_by(Interaction.created_at.desc())
            .limit(3)
            .all()
        )

        previous_sentiment = None
        recurrent_frictions = set()

        if last_interactions:
            # Most recent sentiment
            latest_interaction = last_interactions[0]
            latest_sentiment = (
                db.query(SentimentAnalysis)
                .filter(SentimentAnalysis.interaction_id == latest_interaction.id)
                .first()
            )
            if latest_sentiment:
                previous_sentiment = latest_sentiment.sentiment

            # Aggregate recurring frictions across recent interactions
            recent_ids = [it.id for it in last_interactions]
            frictions = (
                db.query(FrictionPoint.category)
                .filter(FrictionPoint.interaction_id.in_(recent_ids))
                .all()
            )
            for f in frictions:
                recurrent_frictions.add(f[0])

        context = AIContextInput(
            customer_id=customer.external_id,
            tier=customer.tier or "standard",
            historical_summary=customer.historical_summary or "",
            previous_sentiment=previous_sentiment,
            previous_risk_score=customer.current_risk_score,
            recurrent_frictions=list(recurrent_frictions),
            recent_interactions_count=len(last_interactions)
        )

        logger.debug(f"Compact AI context built for customer {customer.external_id}: {context.model_dump()}")
        return context

    @classmethod
    def update_customer_summary(
        cls,
        db: Session,
        customer: Customer,
        new_analysis: AIAnalysisOutput,
        content: str
    ) -> None:
        """
        Updates the customer's compact historical summary incrementally.
        Keeps the summary strictly concise (1-2 sentences) to retain high efficiency.
        """
        frictions_str = ", ".join([f.category for f in new_analysis.friction_points]) if new_analysis.friction_points else "sin fricciones"
        
        if new_analysis.churn_intent:
            new_note = f"[CRÍTICO] Expresó intención de cancelación por: {frictions_str}."
        elif new_analysis.sentiment == "negative":
            new_note = f"[NEGATIVO] Insatisfacción detectada ({new_analysis.emotion}) en: {frictions_str}."
        elif new_analysis.sentiment == "positive":
            new_note = f"[POSITIVO] Interacción satisfactoria reciente."
        else:
            new_note = f"[NEUTRAL] Consulta o comentario general."

        # Keep current summary bounded and relevant
        if not customer.historical_summary:
            customer.historical_summary = new_note
        else:
            # Keep at most last 2 notes to preserve token compactness
            parts = customer.historical_summary.split(" | ")
            if len(parts) >= 2:
                parts = parts[-1:]
            parts.append(new_note)
            customer.historical_summary = " | ".join(parts)

        logger.info(f"Customer {customer.external_id} historical summary updated.")
