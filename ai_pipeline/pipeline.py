"""
Orquestador Principal del Pipeline de Inferencia Semántica y Datos.
Implementa el patrón Local-First / Inferencia en Cascada (Cascaded Inference),
unificando limpieza, PII scrubbing, router de escalado y validación de schemas.
"""

from typing import Optional, Dict, Any
from .schemas import (
    InteractionPayload,
    AISemanticAnalysisResult,
    PIICleanResult,
    SentimentType,
)
from .cleaner import TextCleanerAndPIIScrubber
from .local_nlp_fallback import LocalNLPSentimentEngine
from .cloud_llm import CloudGeminiAnalyzer


class AIPipelineOrchestrator:
    """
    Orquestador del Pipeline de Inteligencia Artificial para el análisis de feedback.
    Asegura máxima velocidad, mínimo costo de tokens y 100% de disponibilidad.
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        gemini_model: str = "gemini-2.5-flash",
        enable_cloud: bool = True,
        confidence_escalation_threshold: float = 0.85,
    ):
        self.cleaner = TextCleanerAndPIIScrubber()
        self.local_engine = LocalNLPSentimentEngine()
        self.enable_cloud = enable_cloud
        self.confidence_escalation_threshold = confidence_escalation_threshold
        
        self.cloud_engine = CloudGeminiAnalyzer(
            api_key=gemini_api_key,
            model_name=gemini_model
        ) if enable_cloud else None

    def process_interaction(self, payload: InteractionPayload) -> AISemanticAnalysisResult:
        """
        Procesa una interacción completa siguiendo el flujo Local-First en cascada:
        1. Limpieza y Sanitización de PII.
        2. Inferencia rápida con Motor Local NLP (<5ms).
        3. Evaluación de escalado al Cloud LLM si el caso es complejo/crítico.
        4. Enriquecimiento de metadata y retorno validado.
        """
        # 1. Sanitización de texto y PII Scrubbing
        pii_result: PIICleanResult = self.cleaner.scrub_pii(payload.message)
        cleaned_text = pii_result.cleaned_text

        # 2. Inferencia Local Ultrarrápida (Fast-Path)
        local_result: AISemanticAnalysisResult = self.local_engine.analyze(cleaned_text)

        # 3. Decisión de Enrutamiento en Cascada
        # Casos que NO necesitan nube (Ahorro de Tokens):
        # - Mensajes positivos o neutros con alta confianza (> 0.85) y sin intención de churn
        is_clear_positive_or_neutral = (
            local_result.sentiment in [SentimentType.POSITIVE, SentimentType.NEUTRAL]
            and not local_result.churn_intent
            and local_result.confidence >= self.confidence_escalation_threshold
        )

        final_result = local_result

        # Si el caso es crítico (negativo, enojo, intención de churn, ambigüedad o cliente Enterprise) y hay nube disponible:
        should_escalate_to_cloud = (
            not is_clear_positive_or_neutral
            or payload.customer_tier == "Enterprise"
            or local_result.churn_intent
        )

        if self.enable_cloud and self.cloud_engine and self.cloud_engine.is_configured and should_escalate_to_cloud:
            cloud_result = self.cloud_engine.analyze(
                sanitized_text=cleaned_text,
                customer_tier=payload.customer_tier
            )
            if cloud_result is not None:
                final_result = cloud_result
            else:
                # Si falló la nube, se añade nota en metadata de fallback
                final_result.processing_metadata["cloud_fallback_triggered"] = True

        # 4. Enriquecer metadata con auditoría de PII y trazabilidad
        final_result.processing_metadata["pii_masked_count"] = pii_result.total_pii_masked
        final_result.processing_metadata["pii_breakdown"] = pii_result.pii_breakdown
        final_result.processing_metadata["was_pii_scrubbed"] = pii_result.was_modified
        final_result.processing_metadata["interaction_id"] = payload.interaction_id
        final_result.processing_metadata["customer_id"] = payload.customer_id
        final_result.processing_metadata["source"] = payload.source.value

        return final_result

    def process_raw_text(
        self,
        text: str,
        customer_id: str = "CUST-ANON",
        interaction_id: str = "INT-RAW",
        customer_tier: str = "Standard"
    ) -> AISemanticAnalysisResult:
        """
        Método de conveniencia para analizar texto directo sin construir manualmente el payload.
        """
        payload = InteractionPayload(
            interaction_id=interaction_id,
            customer_id=customer_id,
            message=text,
            customer_tier=customer_tier
        )
        return self.process_interaction(payload)
