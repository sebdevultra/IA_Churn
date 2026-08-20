import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.core.errors import (
    DuplicateInteractionError,
    EmptyContentError,
    ResourceNotFoundError,
    AIProcessingError
)
from backend.app.models.customer import Customer
from backend.app.models.interaction import Interaction
from backend.app.models.sentiment import SentimentAnalysis
from backend.app.models.friction import FrictionPoint
from backend.app.models.churn_risk import ChurnRisk
from backend.app.models.log import ProcessingLog

from backend.app.schemas.interaction import InteractionCreate
from backend.app.schemas.ai_response import AIAnalysisOutput
from backend.app.services.deduplication import DeduplicationService
from backend.app.services.context_manager import ContextManagerService
from backend.app.services.ai_service import get_ai_provider
from backend.app.services.risk_engine import RiskEngine
from backend.app.services.alert_service import AlertService


class IngestionPipelineService:
    """
    End-to-End Multistage Pipeline Service.
    Orchestrates ingestion, deduplication, AI analysis, deterministic risk calculation,
    alert creation, and audit logging.
    """

    @classmethod
    def get_or_create_customer(
        cls,
        db: Session,
        customer_external_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        tier: str = "standard"
    ) -> Customer:
        """Finds customer by external_id or creates a new one automatically."""
        clean_ext_id = customer_external_id.strip().upper()
        customer = db.query(Customer).filter(Customer.external_id == clean_ext_id).first()
        if not customer:
            customer = Customer(
                external_id=clean_ext_id,
                name=name or f"Customer {clean_ext_id}",
                email=email or f"{clean_ext_id.lower()}@example.com",
                tier=tier or "standard",
                historical_summary="",
                current_risk_score=0,
                current_risk_level="LOW",
                created_at=datetime.utcnow()
            )
            db.add(customer)
            db.flush()
            logger.info(f"Auto-registered new Customer record for external_id: {clean_ext_id}")
        return customer

    @classmethod
    def process_single_interaction(
        cls,
        db: Session,
        payload: InteractionCreate,
        batch_id: Optional[str] = None
    ) -> Interaction:
        """
        Executes the full 10-step processing pipeline for a single interaction.
        Guarantees idempotency, atomic persistence, and no data loss on AI outages.
        """
        start_time = time.time()
        active_batch_id = batch_id or f"batch-{uuid.uuid4().hex[:12]}"

        # Step 1 & 2: Validate Content
        if not payload.content or not payload.content.strip():
            raise EmptyContentError("El contenido de la interacción no puede estar vacío.")

        # Step 3: Deduplication & SHA-256 Hash
        interaction_hash = DeduplicationService.generate_hash(
            payload.customer_external_id,
            payload.content
        )

        if DeduplicationService.is_duplicate(db, interaction_hash):
            raise DuplicateInteractionError(
                message=f"Interacción duplicada para cliente '{payload.customer_external_id}'.",
                hash_val=interaction_hash
            )

        # Step 4: Resolve Customer Entity
        customer = cls.get_or_create_customer(
            db=db,
            customer_external_id=payload.customer_external_id
        )

        # Step 5: Persist Interaction with PENDING_AI_ANALYSIS state
        interaction = Interaction(
            customer_id=customer.id,
            source_type=payload.source_type,
            content=payload.content.strip(),
            interaction_hash=interaction_hash,
            external_reference_id=payload.external_reference_id,
            status="PENDING_AI_ANALYSIS",
            retry_count=0,
            created_at=datetime.utcnow()
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        # Step 6: AI Analysis with Context Manager & Fallback/Retry Protection
        try:
            interaction.status = "PROCESSING"
            db.commit()

            # Build token-optimized context
            context_input = ContextManagerService.build_compact_context(db, customer)
            ai_provider = get_ai_provider()

            # Execute AI Analysis
            ai_output, prompt_tokens, comp_tokens, model_name = ai_provider.analyze_interaction(
                content=interaction.content,
                context=context_input
            )

            # Step 7: Deterministic Risk Engine calculation
            risk_result = RiskEngine.calculate_risk(
                db=db,
                customer=customer,
                ai_output=ai_output
            )

            # Step 8: Persist Results
            # A. Sentiment record
            sentiment_record = SentimentAnalysis(
                interaction_id=interaction.id,
                sentiment=ai_output.sentiment,
                emotion=ai_output.emotion,
                churn_intent=ai_output.churn_intent,
                confidence=ai_output.confidence,
                evidence=ai_output.evidence,
                raw_llm_response=ai_output.model_dump(),
                prompt_tokens=prompt_tokens,
                completion_tokens=comp_tokens,
                model_name=model_name,
                created_at=datetime.utcnow()
            )
            db.add(sentiment_record)

            # B. Friction records
            for f_item in ai_output.friction_points:
                friction_rec = FrictionPoint(
                    interaction_id=interaction.id,
                    category=f_item.category,
                    description=f_item.description,
                    severity=f_item.severity,
                    created_at=datetime.utcnow()
                )
                db.add(friction_rec)

            # C. Churn risk record
            churn_rec = ChurnRisk(
                customer_id=customer.id,
                interaction_id=interaction.id,
                risk_score=risk_result.final_score,
                risk_level=risk_result.risk_level.value,
                score_breakdown=[f.model_dump() for f in risk_result.breakdown],
                calculated_at=datetime.utcnow()
            )
            db.add(churn_rec)
            db.flush()

            # D. Update Customer profile
            customer.current_risk_score = risk_result.final_score
            customer.current_risk_level = risk_result.risk_level.value
            customer.last_interaction_at = datetime.utcnow()
            ContextManagerService.update_customer_summary(
                db=db,
                customer=customer,
                new_analysis=ai_output,
                content=interaction.content
            )

            # Step 9: Alert Engine Evaluation
            AlertService.evaluate_and_create_alert(
                db=db,
                customer=customer,
                churn_risk=churn_rec,
                risk_result=risk_result
            )

            # Step 10: Complete Interaction Status
            interaction.status = "PROCESSED"
            interaction.processed_at = datetime.utcnow()
            interaction.error_message = None
            db.commit()
            db.refresh(interaction)

            duration_ms = (time.time() - start_time) * 1000
            # Log success audit
            audit_log = ProcessingLog(
                batch_id=active_batch_id,
                step="PIPELINE_COMPLETE",
                status="SUCCESS",
                records_processed=1,
                duplicates_count=0,
                errors_count=0,
                duration_ms=duration_ms,
                details={
                    "interaction_id": interaction.id,
                    "customer_id": customer.external_id,
                    "risk_score": risk_result.final_score,
                    "risk_level": risk_result.risk_level.value,
                    "model_used": model_name
                }
            )
            db.add(audit_log)
            db.commit()

            logger.info(
                f"Interaction #{interaction.id} successfully processed in {duration_ms:.1f}ms. Risk Score: {risk_result.final_score}"
            )
            return interaction

        except Exception as exc:
            db.rollback()
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Error processing interaction #{interaction.id}: {str(exc)}")

            # Update interaction to retryable status without losing the record
            interaction.status = "PENDING_AI_ANALYSIS"
            interaction.retry_count += 1
            interaction.error_message = str(exc)
            db.commit()

            # Record audit failure log
            audit_log = ProcessingLog(
                batch_id=active_batch_id,
                step="PIPELINE_FAILED",
                status="ERROR",
                records_processed=0,
                duplicates_count=0,
                errors_count=1,
                duration_ms=duration_ms,
                details={
                    "interaction_id": interaction.id,
                    "customer_id": customer.external_id,
                    "error": str(exc),
                    "retry_count": interaction.retry_count
                }
            )
            db.add(audit_log)
            db.commit()
            raise exc

    @classmethod
    def retry_pending_interactions(cls, db: Session, max_batch: int = 10) -> int:
        """
        Picks up interactions stuck in PENDING_AI_ANALYSIS or RETRYING and retries them.
        """
        pending_list = (
            db.query(Interaction)
            .filter(
                Interaction.status.in_(["PENDING_AI_ANALYSIS", "RETRYING"]),
                Interaction.retry_count < 5
            )
            .order_by(Interaction.created_at.asc())
            .limit(max_batch)
            .all()
        )

        reprocessed_count = 0
        for it in pending_list:
            customer = it.customer
            try:
                context_input = ContextManagerService.build_compact_context(db, customer)
                ai_provider = get_ai_provider()
                ai_output, prompt_tokens, comp_tokens, model_name = ai_provider.analyze_interaction(
                    content=it.content,
                    context=context_input
                )

                risk_result = RiskEngine.calculate_risk(db=db, customer=customer, ai_output=ai_output)

                sentiment_record = SentimentAnalysis(
                    interaction_id=it.id,
                    sentiment=ai_output.sentiment,
                    emotion=ai_output.emotion,
                    churn_intent=ai_output.churn_intent,
                    confidence=ai_output.confidence,
                    evidence=ai_output.evidence,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=comp_tokens,
                    model_name=model_name
                )
                db.add(sentiment_record)

                for f_item in ai_output.friction_points:
                    db.add(FrictionPoint(
                        interaction_id=it.id,
                        category=f_item.category,
                        description=f_item.description,
                        severity=f_item.severity
                    ))

                churn_rec = ChurnRisk(
                    customer_id=customer.id,
                    interaction_id=it.id,
                    risk_score=risk_result.final_score,
                    risk_level=risk_result.risk_level.value,
                    score_breakdown=[f.model_dump() for f in risk_result.breakdown]
                )
                db.add(churn_rec)
                db.flush()

                customer.current_risk_score = risk_result.final_score
                customer.current_risk_level = risk_result.risk_level.value
                customer.last_interaction_at = datetime.utcnow()

                AlertService.evaluate_and_create_alert(
                    db=db, customer=customer, churn_risk=churn_rec, risk_result=risk_result
                )

                it.status = "PROCESSED"
                it.processed_at = datetime.utcnow()
                it.error_message = None
                db.commit()
                reprocessed_count += 1
            except Exception as e:
                db.rollback()
                it.retry_count += 1
                it.error_message = f"Retry failed: {str(e)}"
                db.commit()

        return reprocessed_count
