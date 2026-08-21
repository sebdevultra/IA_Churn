import os
import sys
import json
import re
import time
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional
import httpx
from openai import OpenAI

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.errors import AIProcessingError
from backend.app.schemas.ai_response import AIAnalysisOutput, AIContextInput, FrictionItem

# Ensure repository root is in sys.path for ai_pipeline imports
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

repo_root_alt = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if repo_root_alt not in sys.path:
    sys.path.insert(0, repo_root_alt)

try:
    from ai_pipeline.pipeline import AIPipelineOrchestrator
    from ai_pipeline.schemas import InteractionPayload, AISemanticAnalysisResult
    AI_PIPELINE_AVAILABLE = True
except Exception as exc:
    logger.warning(f"ai_pipeline package could not be imported directly: {exc}")
    AI_PIPELINE_AVAILABLE = False


SYSTEM_PROMPT = """Eres un motor analítico senior de Customer Success e Inteligencia Artificial especializado en detectar señales de satisfacción, frustración, puntos de fricción y riesgo de abandono (churn).

Debes analizar el feedback del cliente considerando su contexto histórico y devolver EXCLUSIVAMENTE un objeto JSON válido con la siguiente estructura exacta:
{
    "sentiment": "positive" | "neutral" | "negative",
    "emotion": "joy" | "satisfaction" | "neutral" | "frustration" | "anger" | "disappointment",
    "friction_points": [
        {
            "category": "customer_support" | "product_reliability" | "pricing" | "usability" | "billing" | "onboarding" | "performance" | "other",
            "description": "descripción concisa del problema",
            "severity": "low" | "medium" | "high"
        }
    ],
    "churn_intent": true | false,
    "confidence": 0.0 a 1.0,
    "evidence": ["citas textuales exactas del cliente que respaldan el análisis"]
}

REGLAS CRÍTICAS:
1. No inventes porcentajes ni scores numéricos de churn (el cálculo matemático lo realiza el backend).
2. 'churn_intent' debe ser true SOLO si el cliente menciona explícitamente cancelar, rescindir contrato, irse a la competencia o suspender el servicio.
3. Si el mensaje es ambiguo (ej: 'esperaba algo diferente'), clasifícalo como neutral o leve insatisfacción, pero con churn_intent = false.
4. Devuelve ÚNICAMENTE el JSON sin bloques de markdown adicionales ni texto explicativo.
"""


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def analyze_interaction(
        self,
        content: str,
        context: AIContextInput
    ) -> Tuple[AIAnalysisOutput, int, int, str]:
        """
        Analyzes customer interaction.
        Returns (AIAnalysisOutput, prompt_tokens, completion_tokens, model_name).
        """
        pass


class UnifiedAIPipelineProvider(BaseLLMProvider):
    """
    Adapter provider connecting the backend directly to the unified AIPipelineOrchestrator.
    Handles:
    - Text normalization & PII scrubbing (Habeas Data/GDPR compliance)
    - Fast local symbolic & lexical NLP inference (<5ms)
    - Cascaded cloud escalation to Gemini / LLM for critical signals or Enterprise tiers
    - Structured semantic output mapping
    """

    def __init__(self):
        gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.orchestrator = AIPipelineOrchestrator(
            gemini_api_key=gemini_key,
            gemini_model=settings.GEMINI_MODEL,
            enable_cloud=settings.ENABLE_CLOUD_AI,
            confidence_escalation_threshold=settings.CONFIDENCE_ESCALATION_THRESHOLD
        )

    def analyze_interaction(
        self,
        content: str,
        context: AIContextInput
    ) -> Tuple[AIAnalysisOutput, int, int, str]:
        tier_str = (context.tier or "Standard").strip().title()
        if tier_str not in ["Enterprise", "Pro", "Standard"]:
            tier_str = "Enterprise" if "ent" in tier_str.lower() else ("Pro" if "pro" in tier_str.lower() else "Standard")

        payload = InteractionPayload(
            interaction_id=f"INT-{int(time.time()*1000)}",
            customer_id=context.customer_id,
            message=content,
            customer_tier=tier_str,
            customer_history_count=context.recent_interactions_count
        )

        semantic_res: AISemanticAnalysisResult = self.orchestrator.process_interaction(payload)

        # Map frictions to FrictionItem
        friction_items = []
        for f in semantic_res.friction_points:
            cat_val = f.value if hasattr(f, "value") else str(f)
            if cat_val != "none":
                friction_items.append(FrictionItem(
                    category=cat_val,
                    description=f"Punto de fricción identificado en {cat_val.replace('_', ' ')}",
                    severity="high" if semantic_res.churn_intent or (hasattr(semantic_res.emotion, "value") and semantic_res.emotion.value in ["anger", "anxiety"]) else "medium"
                ))

        sentiment_val = semantic_res.sentiment.value if hasattr(semantic_res.sentiment, "value") else str(semantic_res.sentiment)
        emotion_val = semantic_res.emotion.value if hasattr(semantic_res.emotion, "value") else str(semantic_res.emotion)

        output = AIAnalysisOutput(
            sentiment=sentiment_val,
            emotion=emotion_val,
            friction_points=friction_items,
            churn_intent=semantic_res.churn_intent,
            is_sarcastic=bool(semantic_res.processing_metadata.get("is_sarcastic", False)),
            confidence=semantic_res.confidence,
            evidence=semantic_res.evidence
        )

        engine_used = semantic_res.processing_metadata.get("engine_used", "local_nlp")
        prompt_tokens = len(content.split()) + 35
        completion_tokens = 50

        return output, prompt_tokens, completion_tokens, engine_used


class DeterministicRuleAIProvider(BaseLLMProvider):
    """
    High-precision local deterministic semantic provider.
    Enables offline demo, fast integration testing, and zero-cost local execution
    while strictly complying with the Pydantic structured output contract.
    """

    def analyze_interaction(
        self,
        content: str,
        context: AIContextInput
    ) -> Tuple[AIAnalysisOutput, int, int, str]:
        lower_content = content.lower().strip()

        # 1. Detect explicit Churn Intent
        churn_keywords = [
            "cancelar", "cancelo", "cancelaré", "darme de baja", "doy de baja",
            "irme a la competencia", "no renovaré", "no renovar", "dejar de usar",
            "cerrar mi cuenta", "cancel subscription", "churn", "leaving", "switch to competitor"
        ]
        has_churn_intent = any(kw in lower_content for kw in churn_keywords)

        # 2. Detect Positive Signals
        positive_keywords = [
            "excelente", "satisfecho", "satisfacción", "genial", "gran trabajo",
            "me encanta", "perfecto", "maravilla", "felicitaciones", "muy buen",
            "buen servicio", "great", "excellent", "love", "satisfied", "amazing"
        ]
        has_positive = any(kw in lower_content for kw in positive_keywords)

        # 3. Detect Negative / Frustration Signals
        frustration_keywords = [
            "harto", "cansado", "esperar días", "días esperando", "pésimo",
            "inaceptable", "enojado", "molesto", "terrible", "vergüenza",
            "frustrated", "awful", "horrible", "angry", "waste of time"
        ]
        has_frustration = any(kw in lower_content for kw in frustration_keywords)

        # 4. Detect Ambiguous / Mild Signals
        ambiguous_keywords = [
            "esperaba algo diferente", "bueno...", "no sé", "regular", "mas o menos",
            "podría ser mejor", "veremos", "meh"
        ]
        is_ambiguous = any(kw in lower_content for kw in ambiguous_keywords)

        # Friction detection
        frictions = []
        evidence = []

        if any(w in lower_content for w in ["soporte", "atención", "ticket", "tardanza", "responder", "agente", "support", "helpdesk"]):
            frictions.append(FrictionItem(
                category="customer_support",
                description="Problemas o demoras en la atención de soporte técnico",
                severity="high" if has_frustration else "medium"
            ))
            evidence.append("Mención de lentitud o deficiencias en soporte")

        if any(w in lower_content for w in ["caída", "bug", "error", "falla", "caído", "lento", "rendimiento", "down", "crash", "performance"]):
            frictions.append(FrictionItem(
                category="product_reliability",
                description="Inestabilidad o fallos recurrentes en la plataforma",
                severity="high" if has_frustration else "medium"
            ))
            evidence.append("Reporte de fallas técnicas o bugs en el sistema")

        if any(w in lower_content for w in ["precio", "caro", "costo", "tarifa", "factura", "facturación", "cobro", "billing", "invoice"]):
            frictions.append(FrictionItem(
                category="billing",
                description="Disconformidad con tarifas, cargos o facturación",
                severity="medium"
            ))
            evidence.append("Disconformidad con costos o proceso de facturación")

        # Determine Sentiment and Emotion
        if has_churn_intent:
            sentiment = "negative"
            emotion = "frustration"
            evidence.append(f"Intención explícita de cancelación: '{content}'")
            confidence = 0.95
        elif has_frustration or (frictions and not has_positive):
            sentiment = "negative"
            emotion = "anger" if any(w in lower_content for w in ["inaceptable", "pésimo", "vergüenza"]) else "frustration"
            evidence.append(f"Expresión de frustración: '{content}'")
            confidence = 0.92
        elif has_positive:
            sentiment = "positive"
            emotion = "joy" if "me encanta" in lower_content or "felicitaciones" in lower_content else "satisfaction"
            evidence.append(f"Comentarios favorables: '{content}'")
            confidence = 0.94
        elif is_ambiguous:
            sentiment = "neutral"
            emotion = "neutral"
            evidence.append(f"Feedback ambiguo o moderado: '{content}'")
            confidence = 0.75
        else:
            sentiment = "neutral"
            emotion = "neutral"
            confidence = 0.70
            if content:
                evidence.append(content[:100])

        output = AIAnalysisOutput(
            sentiment=sentiment,
            emotion=emotion,
            friction_points=frictions,
            churn_intent=has_churn_intent,
            confidence=confidence,
            evidence=evidence
        )

        prompt_tokens = len(content.split()) + 40
        completion_tokens = 60
        model_name = "deterministic-rule-v1"

        return output, prompt_tokens, completion_tokens, model_name


class OpenAILLMProvider(BaseLLMProvider):
    """
    OpenAI and OpenAI-compatible (Gemini / DeepSeek / Ollama) cloud LLM provider.
    Includes JSON schema enforcement, sanitization heuristic, and retry mechanism.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.base_url = settings.OPENAI_BASE_URL
        self.max_retries = settings.AI_MAX_RETRIES
        self.timeout = settings.AI_TIMEOUT_SECONDS

        if not self.api_key:
            logger.warning("OPENAI_API_KEY is not configured. Real API calls may fail.")

        self.client = OpenAI(
            api_key=self.api_key or "dummy_key",
            base_url=self.base_url,
            timeout=self.timeout
        )

    def _sanitize_and_repair_json(self, raw_text: str) -> dict:
        cleaned = raw_text.strip()
        if "```" in cleaned:
            cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not parse valid JSON from AI response: {raw_text[:200]}")

    def analyze_interaction(
        self,
        content: str,
        context: AIContextInput
    ) -> Tuple[AIAnalysisOutput, int, int, str]:
        user_message = f"""CONTEXTO DEL CLIENTE:
{context.model_dump_json(indent=2)}

NUEVO MENSAJE/INTERACCIÓN A ANALIZAR:
"{content}"
"""

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Invoking LLM ({self.model}) - Attempt {attempt}/{self.max_retries}")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )

                raw_content = response.choices[0].message.content
                prompt_tokens = response.usage.prompt_tokens if response.usage else 120
                completion_tokens = response.usage.completion_tokens if response.usage else 50

                parsed_json = self._sanitize_and_repair_json(raw_content)
                validated_output = AIAnalysisOutput.model_validate(parsed_json)

                return validated_output, prompt_tokens, completion_tokens, self.model

            except Exception as exc:
                last_error = exc
                logger.warning(f"LLM call attempt {attempt} failed: {str(exc)}")
                if attempt < self.max_retries:
                    sleep_time = (2 ** (attempt - 1)) * 0.5
                    time.sleep(sleep_time)

        raise AIProcessingError(
            message=f"Exhausted {self.max_retries} attempts: {str(last_error)}",
            provider="openai_compatible",
            details={"last_error": str(last_error)}
        )


def get_ai_provider() -> BaseLLMProvider:
    """
    Factory function returning the configured LLM provider.
    Defaults to UnifiedAIPipelineProvider if ai_pipeline is available.
    """
    if AI_PIPELINE_AVAILABLE and settings.AI_PROVIDER in ["ai_pipeline", "gemini", "deterministic_rule"]:
        logger.info(f"Initializing Unified AIPipelineProvider (Local-First + Cascaded Gemini, Cloud={settings.ENABLE_CLOUD_AI}).")
        return UnifiedAIPipelineProvider()
    elif settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        logger.info("Initializing OpenAI Cloud LLM Provider.")
        return OpenAILLMProvider()
    else:
        logger.info(f"Using Deterministic Rule-Based Local AI Provider (AI_PROVIDER='{settings.AI_PROVIDER}').")
        return DeterministicRuleAIProvider()

