"""
Módulo de Schemas y Modelos de Datos Pydantic para el Pipeline de IA.
Define los contratos de datos inmutables y validados para la ingesta y extracción semántica.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator



class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class EmotionType(str, Enum):
    SATISFACTION = "satisfaction"
    NEUTRAL = "neutral"
    CONFUSION = "confusion"
    FRUSTRATION = "frustration"
    ANGER = "anger"


class FrictionCategory(str, Enum):
    BILLING_PRICING = "billing_pricing"
    PRODUCT_RELIABILITY = "product_reliability"
    CUSTOMER_SUPPORT = "customer_support"
    FEATURE_GAP = "feature_gap"
    SLA_DELAY = "sla_delay"
    NONE = "none"


class InteractionSource(str, Enum):
    SUPPORT_TICKET = "support_ticket"
    REVIEW = "review"
    NPS_SURVEY = "nps_survey"
    CHAT = "chat"


class InteractionPayload(BaseModel):
    """
    Estructura de entrada para cualquier mensaje o interacción de cliente
    antes de ser procesada por el pipeline de IA.
    """
    interaction_id: str = Field(
        ...,
        description="Identificador único de la interacción (UUID o formato INT-XXXX)",
        examples=["INT-88392"]
    )
    customer_id: str = Field(
        ...,
        description="Identificador único del cliente (UUID o formato CUST-XXXX)",
        examples=["CUST-1042"]
    )
    source: InteractionSource = Field(
        default=InteractionSource.SUPPORT_TICKET,
        description="Canal de origen del feedback"
    )
    message: str = Field(
        ...,
        description="Texto no estructurado del cliente",
        min_length=0
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp de emisión del mensaje"
    )
    customer_history_count: int = Field(
        default=0,
        ge=0,
        description="Cantidad de interacciones negativas previas del cliente en últimos 30 días"
    )
    customer_tier: Literal["Enterprise", "Pro", "Standard"] = Field(
        default="Standard",
        description="Nivel o segmento de valor del cliente"
    )

    @field_validator("message")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class PIICleanResult(BaseModel):
    """
    Resultado del proceso de sanitización y enmascaramiento de datos sensibles (PII).
    """
    original_text: str
    cleaned_text: str
    pii_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Conteo de entidades sensibles enmascaradas por tipo"
    )
    total_pii_masked: int = Field(
        default=0,
        ge=0,
        description="Número total de elementos sensibles sustituidos"
    )
    was_modified: bool = False


class AISemanticAnalysisResult(BaseModel):
    """
    Contrato estricto de salida del Pipeline de IA.
    Entrega señales semánticas estructuradas al Risk Engine del Backend.
    """
    sentiment: SentimentType = Field(
        ...,
        description="Polaridad general del mensaje (positive, neutral, negative)"
    )
    emotion: EmotionType = Field(
        ...,
        description="Emoción subyacente predominante"
    )
    friction_points: List[FrictionCategory] = Field(
        default_factory=list,
        description="Categorías de fricción u origen del problema detectadas"
    )
    churn_intent: bool = Field(
        ...,
        description="Indica si existe intención explícita o sutil de cancelar/abandonar el servicio"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Nivel de certidumbre del análisis semántico entre 0.0 y 1.0"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Frases literales o fragmentos clave que sustentan la clasificación"
    )
    processing_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadatos operativos: engine_used ('local_nlp'|'cloud_gemini'), latency_ms, pii_count, etc."
    )

    @field_validator("friction_points")
    @classmethod
    def ensure_friction_list_not_empty_unless_none(cls, v: List[FrictionCategory]) -> List[FrictionCategory]:
        if not v:
            return [FrictionCategory.NONE]
        # Si contiene categorías reales, remover NONE si está presente
        if len(v) > 1 and FrictionCategory.NONE in v:
            v = [cat for cat in v if cat != FrictionCategory.NONE]
        return list(dict.fromkeys(v))  # Remover duplicados preservando orden
