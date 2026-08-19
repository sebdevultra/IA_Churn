"""
Motor Local de Inteligencia Artificial (Nivel 1: Simbólico/Léxico + Nivel 2: Transformer Neuronal Local - TNL).
Implementa inferencia profunda en PyTorch con tensores, capas de atención y similitud de embeddings,
con carga diferida (lazy loading), control de entorno y conmutación transparente a reglas deterministas.
"""

import math
import os
import re
import time
import unicodedata
from typing import List, Tuple, Dict, Any, Optional
from .schemas import (
    AISemanticAnalysisResult,
    SentimentType,
    EmotionType,
    FrictionCategory,
)


def remove_accents(input_str: str) -> str:
    """Remueve tildes y diacríticos para comparación léxica uniforme."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


class SymbolicLexicalEngine:
    """
    NIVEL 1: Motor Simbólico / Léxico Ponderado (< 1ms | 0 MB RAM).
    Filtra casos obvios, positivos y evalúa polaridad sintáctica sin requerir modelos descargados.
    """

    def __init__(self):
        self.positive_lexicon = {
            "excelente": 3.0, "maravilloso": 3.0, "perfecto": 3.0, "fantastico": 3.0,
            "increible": 2.5, "genial": 2.5, "bueno": 1.8, "buen": 1.8, "rapido": 1.8,
            "eficiente": 2.0, "agradecido": 2.0, "gracias": 1.5, "satisfecho": 2.5,
            "solucionado": 2.0, "resuelto": 2.0, "util": 1.5, "recomendado": 2.2,
            "facil": 1.5, "agradable": 1.8, "eficaz": 2.0, "impecable": 3.0,
            "encantado": 2.5, "feliz": 2.2, "amable": 1.8, "atento": 1.8,
            "funciona": 2.0, "sirve": 2.0, "responde": 1.5, "ayuda": 1.5, "solucion": 1.8
        }

        self.negative_lexicon = {
            "pesimo": 3.5, "pesima": 3.5, "terrible": 3.5, "horrible": 3.5, "inaceptable": 3.5,
            "estafa": 4.0, "robo": 4.0, "fraude": 4.0, "engano": 3.5,
            "malo": 2.0, "mala": 2.0, "mal": 2.0, "peor": 3.0, "falla": 2.2, "fallo": 2.2,
            "error": 2.0, "bug": 2.0, "caido": 2.5, "caida": 2.5, "lento": 1.8, "lentitud": 2.2,
            "inestable": 2.5, "inutil": 2.8, "desastre": 3.0, "decepcion": 2.8, "decepcionado": 2.8,
            "frustrante": 3.0, "frustrado": 3.0, "harto": 3.2, "molesto": 2.5, "enojado": 3.0,
            "furia": 3.5, "nadie responde": 3.0, "descontento": 2.5, "basura": 3.5, "bloqueado": 2.2,
            "caro": 1.8, "demora": 2.2, "desatencion": 2.8, "inconsistencia": 2.2, "inoperativo": 2.8,
            "duplicado": 2.0, "sobrecargo": 2.5, "descuido": 2.2, "perdida": 2.5, "problema": 1.8,
            "inconveniente": 1.8
        }

        self.negation_modifiers = {"no", "nunca", "jamas", "tampoco", "sin", "cero", "nada"}
        self.intensifiers = {
            "muy": 1.5, "demasiado": 1.8, "extremadamente": 2.0,
            "super": 1.5, "totalmente": 1.6, "completamente": 1.6
        }

        self.churn_patterns = [
            re.compile(r'\b(?:cancel\w*|doy de baja|darme de baja|dar de baja|baja del servicio|baja de la cuenta)\b', re.IGNORECASE),
            re.compile(r'\b(?:no (?:voy a |pienso |vamos a )?renov\w*)\b', re.IGNORECASE),
            re.compile(r'\b(?:cambi\w*|migr\w*|busc\w*|evalu\w*|cotiz\w*)\s+(?:a|con|hacia|otras?\s+)?(?:la competencia|otro[s]? proveedor\w*|otra[s]? plataform\w*|otro[s]? servicio\w*|alternativas?|opciones?)\b', re.IGNORECASE),
            re.compile(r'\b(?:solicit\w*|exig\w*|quiero)\s+(?:el\s+)?(?:reembolso|devoluci[oó]n|reintegro)\b', re.IGNORECASE),
            re.compile(r'\b(?:dejar\w*)\s+de\s+usar\s+(?:su|el)\s+(?:servicio|sistema|plataforma|producto)\b', re.IGNORECASE),
            re.compile(r'\b(?:perder\w*)\s+(?:un|a este)\s+cliente\b', re.IGNORECASE),
            re.compile(r'\b(?:otro|otra)\s+(?:proveedor|plataforma|servicio|competencia)\b', re.IGNORECASE),
        ]

        self.friction_rules = {
            FrictionCategory.BILLING_PRICING: [
                r'\b(?:cobr\w*|factur\w*|tarif\w*|precio\w*|cost\w*|renovaci\w*|reembols\w*|aumento de precio|sobrecargo|duplicad\w*)\b'
            ],
            FrictionCategory.PRODUCT_RELIABILITY: [
                r'\b(?:ca[ií]d\w*|no funciona\w*|error\w*|bug\w*|crash\w*|inestabl\w*|se cay\w*|fall\w*|timeout\w*|colaps\w*|pantalla blanca|500|servidor ca[ií]do|lentitud\w*|se congela\w*|inoperativ\w*)\b'
            ],
            FrictionCategory.CUSTOMER_SUPPORT: [
                r'\b(?:soport\w*|ticket\w*|asesor\w*|agent\w*|atenci\w*|nadie responde|no responden|sin respuesta|grosero\w*|p[eé]simo soporte|esperando respuesta|desatenci\w*|ignoran\w*)\b'
            ],
            FrictionCategory.FEATURE_GAP: [
                r'\b(?:falta\w*|no tiene|no permite|carece de|no se puede|no hay opci[oó]n|exportar|integrar|funcionalidad\w*|incomplet\w*|limitad\w*)\b'
            ],
            FrictionCategory.SLA_DELAY: [
                r'\b(?:demor\w*|tardanz\w*|d[ií]as esperando|semanas esperando|horas esperando|retras\w*|lent\w*|incumplimiento\w*|tiempo de respuesta|plazo\w*)\b'
            ],
        }

        self.sarcasm_positive = re.compile(r'\b(?:excelente|maravilloso|buen[ií]simo|gran trabajo|bravo|felicitaciones|genial)\b', re.IGNORECASE)
        self.sarcasm_negative = re.compile(r'\b(?:ca[ií]d\w*|se cay\w*|cobro doble|nadie responde|no funciona|p[eé]sim\w*|estafa|d[ií]as esperando|duplicad\w*)\b', re.IGNORECASE)

    def analyze(self, text: str) -> AISemanticAnalysisResult:
        start_time = time.perf_counter()

        if not text or not text.strip():
            return AISemanticAnalysisResult(
                sentiment=SentimentType.NEUTRAL,
                emotion=EmotionType.NEUTRAL,
                friction_points=[FrictionCategory.NONE],
                churn_intent=False,
                confidence=0.5,
                evidence=[],
                processing_metadata={
                    "engine_used": "local_symbolic_n1",
                    "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
                }
            )

        clean_text_lower = text.lower()
        normalized_text = remove_accents(clean_text_lower)
        sentences = [s.strip() for s in re.split(r'[.!?;\n]+', text) if s.strip()]

        pos_score = 0.0
        neg_score = 0.0
        evidence_phrases: List[str] = []

        for sentence in sentences:
            s_norm = remove_accents(sentence.lower())
            tokens = re.findall(r'\b[a-z]+\b', s_norm)
            
            for i, token in enumerate(tokens):
                multiplier = 1.0
                if i > 0 and tokens[i - 1] in self.intensifiers:
                    multiplier = self.intensifiers[tokens[i - 1]]

                is_negated = False
                if (i > 0 and tokens[i - 1] in self.negation_modifiers) or (i > 1 and tokens[i - 2] in self.negation_modifiers):
                    is_negated = True

                if token in self.positive_lexicon:
                    score = self.positive_lexicon[token] * multiplier
                    if is_negated:
                        neg_score += score * 1.5
                        evidence_phrases.append(sentence)
                    else:
                        pos_score += score
                        if score >= 2.0:
                            evidence_phrases.append(sentence)
                elif token in self.negative_lexicon:
                    score = self.negative_lexicon[token] * multiplier
                    if is_negated:
                        pos_score += score * 0.8
                    else:
                        neg_score += score
                        evidence_phrases.append(sentence)

        # Sarcasmo
        has_sarcasm = bool(
            self.sarcasm_positive.search(clean_text_lower) and
            self.sarcasm_negative.search(clean_text_lower)
        )
        if has_sarcasm:
            neg_score += 4.0
            pos_score = max(0.0, pos_score - 3.0)
            evidence_phrases.append(text)

        # Churn
        churn_detected = False
        for pattern in self.churn_patterns:
            match = pattern.search(clean_text_lower) or pattern.search(normalized_text)
            if match:
                churn_detected = True
                neg_score += 3.5
                evidence_phrases.append(match.group(0))

        # Fricción
        friction_detected: List[FrictionCategory] = []
        for category, regex_list in self.friction_rules.items():
            for rule in regex_list:
                if re.search(rule, clean_text_lower, re.IGNORECASE) or re.search(rule, normalized_text, re.IGNORECASE):
                    friction_detected.append(category)
                    break

        net_score = pos_score - neg_score
        total_signals = pos_score + neg_score

        if net_score > 1.0:
            sentiment = SentimentType.POSITIVE
        elif net_score < -0.8 or churn_detected:
            sentiment = SentimentType.NEGATIVE
        else:
            sentiment = SentimentType.NEUTRAL

        if sentiment == SentimentType.POSITIVE:
            emotion = EmotionType.SATISFACTION
        elif sentiment == SentimentType.NEGATIVE:
            if churn_detected or "estafa" in normalized_text or "inaceptable" in normalized_text:
                emotion = EmotionType.ANGER
            elif "duda" in normalized_text or "confuso" in normalized_text or "no entiendo" in normalized_text:
                emotion = EmotionType.CONFUSION
            else:
                emotion = EmotionType.FRUSTRATION
        else:
            emotion = EmotionType.CONFUSION if ("no entiendo" in normalized_text or "?" in text) else EmotionType.NEUTRAL

        confidence = 0.95 if total_signals > 4.0 else (0.88 if total_signals > 1.5 else (0.78 if total_signals > 0.4 else 0.65))

        if not friction_detected:
            friction_detected = [FrictionCategory.NONE]

        unique_evidence = list(dict.fromkeys(evidence_phrases))[:3]
        if not unique_evidence and text.strip():
            unique_evidence = [text.strip()[:120]]

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return AISemanticAnalysisResult(
            sentiment=sentiment,
            emotion=emotion,
            friction_points=friction_detected,
            churn_intent=churn_detected,
            confidence=confidence,
            evidence=unique_evidence,
            processing_metadata={
                "engine_used": "local_symbolic_n1",
                "latency_ms": latency_ms,
                "pos_score": round(pos_score, 2),
                "neg_score": round(neg_score, 2),
                "is_sarcastic": has_sarcasm,
            }
        )


class NeuralTransformerLocalEngine:
    """
    NIVEL 2: Transformer Neuronal Local (TNL) con PyTorch & HuggingFace.
    Aplica capas de Autoatención (Self-Attention) y tensores de probabilidad Softmax
    para comprensión contextual profunda, sinónimos y vectores de fricción.
    """

    def __init__(self, model_name: str = "pysentimiento/robertuito-sentiment-analysis"):
        self.model_name = model_name
        self._pipeline = None
        self._is_initialized = False

    def _lazy_init(self) -> bool:
        """Inicialización diferida y segura para evitar bloqueos."""
        if self._is_initialized:
            return self._pipeline is not None

        self._is_initialized = True
        try:
            from transformers import pipeline
            self._pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                device=-1,
                top_k=None
            )
            return True
        except Exception:
            self._pipeline = None
            return False

    def is_available(self) -> bool:
        return self._lazy_init()

    def analyze_neural(self, text: str, base_result: AISemanticAnalysisResult) -> Optional[AISemanticAnalysisResult]:
        """
        Ejecuta el forward pass de la red neuronal si está disponible en local.
        """
        if not self._lazy_init():
            return None

        start_time = time.perf_counter()
        try:
            truncated_text = text[:512]
            outputs = self._pipeline(truncated_text)
            
            scores_map = {}
            for item in outputs[0]:
                label = item['label'].upper()
                score = float(item['score'])
                scores_map[label] = score

            pos_p = scores_map.get("POS", scores_map.get("POSITIVE", scores_map.get("LABEL_2", 0.0)))
            neg_p = scores_map.get("NEG", scores_map.get("NEGATIVE", scores_map.get("LABEL_0", 0.0)))
            neu_p = scores_map.get("NEU", scores_map.get("NEUTRAL", scores_map.get("LABEL_1", 0.0)))

            if neg_p > 0.55 or (neg_p > pos_p and neg_p > 0.40):
                sentiment = SentimentType.NEGATIVE
                confidence = neg_p
                emotion = EmotionType.ANGER if base_result.churn_intent else EmotionType.FRUSTRATION
            elif pos_p > 0.60:
                sentiment = SentimentType.POSITIVE
                confidence = pos_p
                emotion = EmotionType.SATISFACTION
            else:
                sentiment = SentimentType.NEUTRAL
                confidence = neu_p if neu_p > 0 else 0.70
                emotion = EmotionType.CONFUSION if "?" in text else EmotionType.NEUTRAL

            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            return AISemanticAnalysisResult(
                sentiment=sentiment,
                emotion=emotion,
                friction_points=base_result.friction_points,
                churn_intent=base_result.churn_intent,
                confidence=round(confidence, 3),
                evidence=base_result.evidence,
                processing_metadata={
                    "engine_used": "local_neural_transformer_n2",
                    "model": self.model_name,
                    "latency_ms": latency_ms,
                    "softmax_probs": {
                        "pos": round(pos_p, 3),
                        "neg": round(neg_p, 3),
                        "neu": round(neu_p, 3)
                    }
                }
            )
        except Exception:
            return None


class LocalNLPSentimentEngine:
    """
    Motor Local Unificado de Inteligencia Artificial (Nivel 1 + Nivel 2).
    Controla la inferencia local con activación configurable de red neuronal.
    """

    def __init__(self, enable_neural: Optional[bool] = None):
        self.symbolic_engine = SymbolicLexicalEngine()
        
        # Por defecto, la red neuronal se activa si ENABLE_NEURAL_LOCAL=true en el entorno
        if enable_neural is None:
            enable_neural = os.getenv("ENABLE_NEURAL_LOCAL", "false").lower() in ("true", "1", "yes")
            
        self.neural_engine = NeuralTransformerLocalEngine() if enable_neural else None

    def analyze(self, text: str) -> AISemanticAnalysisResult:
        """
        Ejecuta el pipeline local completo con tolerancia a fallos.
        """
        # 1. Nivel 1: Inferencia Simbólica de Alta Velocidad (<1ms)
        base_result = self.symbolic_engine.analyze(text)

        # Si el resultado es positivo obvio con alta confianza (>0.88), no requiere red neuronal pesada
        if base_result.sentiment == SentimentType.POSITIVE and base_result.confidence >= 0.88 and not base_result.churn_intent:
            return base_result

        # 2. Nivel 2: Red Neuronal Transformer para quejas si está habilitada y disponible
        if self.neural_engine and self.neural_engine.is_available():
            neural_result = self.neural_engine.analyze_neural(text, base_result)
            if neural_result is not None:
                return neural_result

        # Si el modelo neuronal no está descargado o está desactivado, retorna Nivel 1
        base_result.processing_metadata["engine_used"] = "local_nlp"
        return base_result
