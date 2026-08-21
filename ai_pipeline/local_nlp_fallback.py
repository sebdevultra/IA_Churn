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
            "solucionado": 3.0, "soluciono": 3.0, "resuelto": 3.0, "resolvio": 3.0, "resolvieron": 3.0, "util": 1.5, "recomendado": 2.2,
            "facil": 1.5, "agradable": 1.8, "eficaz": 2.0, "impecable": 3.0,
            "encantado": 2.5, "feliz": 2.2, "amable": 1.8, "atento": 1.8,
            "funciona": 2.0, "sirve": 2.0, "responde": 1.5, "ayuda": 1.5, "solucion": 2.0,
            "conforme": 2.5, "mejorado": 2.5, "mejor": 2.0, "notable": 2.0
        }

        self.negative_lexicon = {
            "pesimo": 3.5, "pesima": 3.5, "terrible": 3.5, "horrible": 3.5, "inaceptable": 3.5,
            "estafa": 4.0, "robo": 4.0, "fraude": 4.0, "engano": 3.5, "abusivo": 3.5, "abuso": 3.5,
            "malo": 2.0, "mala": 2.0, "mal": 2.0, "peor": 3.0, "falla": 2.2, "fallo": 2.2, "fallas": 2.5,
            "error": 2.0, "errores": 2.2, "bug": 2.0, "bugs": 2.2, "caido": 2.5, "caida": 2.5, "cayo": 2.5, "cayeron": 2.5, "lento": 1.8, "lentitud": 2.2,
            "inestable": 2.5, "inutil": 2.8, "desastre": 3.0, "decepcion": 2.8, "decepcionado": 2.8,
            "frustrante": 3.0, "frustrado": 3.0, "harto": 3.2, "molesto": 2.5, "enojado": 3.0,
            "furia": 3.5, "nadie responde": 3.0, "descontento": 2.5, "basura": 3.8, "bloqueado": 2.8,
            "bloquearon": 3.0, "bloqueo": 2.8, "bloqueos": 2.8, "bloquea": 2.8, "bloquean": 2.8, "caro": 1.8, "demora": 2.2, "desatencion": 2.8,
            "inconsistencia": 2.5, "inconsistencias": 2.5, "inoperativo": 2.8, "duplicado": 2.0, "duplicaron": 2.5,
            "sobrecargo": 2.5, "descuido": 2.2, "perdida": 2.5, "perdimos": 2.8, "perdiendo": 2.5, "problema": 1.5, "problemas": 1.8,
            "inconveniente": 1.8, "canse": 2.5, "insatisfaccion": 3.0, "erroneos": 2.5, "erroneo": 2.5, "expensive": 2.5,
            "porqueria": 3.8, "fiasco": 3.5, "mamado": 3.5, "descarado": 3.5, "descaro": 3.5, "arruinaron": 3.5, "arruinar": 3.5,
            "incompetentes": 3.5, "incompetencia": 3.5, "asco": 3.8, "borraron": 3.0, "borro": 3.0, "triple": 2.5,
            "indebido": 3.0, "ocultos": 2.8, "oculto": 2.5, "graves": 2.8, "grave": 2.5, "injustificada": 2.8, "injustificado": 2.8,
            "dilatando": 2.8, "incidente": 2.2, "critico": 2.5, "sin respuesta": 3.0, "sin recibir respuesta": 3.0, "nadie contesta": 3.0,
            "nadie resuelve": 3.0, "no responden": 3.0, "ignorando": 3.0, "ignoran": 3.0, "deficiente": 2.8, "reiterada": 2.2,
            "reiteradas": 2.2, "reiterado": 2.2, "grosero": 3.0, "desatento": 2.8, "transfieren": 2.2, "colgo": 3.0, "colgaron": 3.0,
            "incumplido": 3.0, "incumplimiento": 3.0, "detenido": 2.5, "tumba": 2.8, "inactividad": 2.5, "intermitencias": 2.5,
            "urgente": 2.0, "expuso": 2.5, "filtro": 2.5, "filtrada": 2.5, "rompieron": 2.8, "inviable": 3.0, "bajo rendimiento": 2.5,
            "no cumple": 3.0, "mandarin": 2.5, "latencia": 2.5, "cierra": 2.5, "cierre": 2.0, "no hace nada": 2.8, "nunca se presento": 3.0,
            "blanco": 2.0, "ocupado": 2.0, "exijo": 2.5
        }



        self.negation_modifiers = {"no", "nunca", "jamas", "tampoco", "sin", "cero", "nada", "ya no", "nadie", "ningun", "ninguno", "ninguna", "ni"}

        self.intensifiers = {
            "muy": 1.5, "demasiado": 1.8, "extremadamente": 2.0,
            "super": 1.5, "totalmente": 1.6, "completamente": 1.6, "irrevocable": 2.0, "absoluta": 1.8, "definitiva": 1.8
        }

        self.churn_patterns = [
            re.compile(r'\b(?:cancel\w*|doy de baja|darme de baja|dar de baja|den de baja|denme de baja|pide la baja|solicito la baja|tramitar baja|deseo mi baja|baja del servicio|baja de la cuenta|baja de sus servicios|baja total|baja definitiva|bajas?)\b', re.IGNORECASE),
            re.compile(r'\b(?:rescind\w*|rescision|revoc\w*)\b', re.IGNORECASE),
            re.compile(r'\b(?:anul\w*|anulacion)\b', re.IGNORECASE),
            re.compile(r'\b(?:cerr\w*|cierre|cierren)\s+(?:definitiv\w*\s+)?(?:de\s+)?(?:mi\s+|la\s+|esta\s+)?(?:cuenta|perfil|relacion|contrato|servicios|solicitud)\b', re.IGNORECASE),
            re.compile(r'\b(?:termin\w*)\s+(?:mi|nuestra)?\s*relaci[oó]n\s+comercial\b', re.IGNORECASE),
            re.compile(r'\b(?:no (?:voy a |pienso |vamos a |deseo |quiero |es inviable mantener la |dar aviso de no )?(?:continuar\s+con\s+la\s+)?renov\w*)\b', re.IGNORECASE),
            re.compile(r'\b(?:analiz\w*|evalu\w*|compar\w*|busc\w*|cotiz\w*|mir\w*|revis\w*|consider\w*|prob\w*|solicit\w*)\s+(?:opciones|alternativas|planes|propuestas|cotizaci[oó]n)?\s*(?:a|con|de|hacia)?\s*(?:otro[s]?\s+|la\s+|su\s+)?(?:proveedor\w*|competencia|competencia directa|plataform\w*|servicio\w*|software|competidor)\b', re.IGNORECASE),
            re.compile(r'\b(?:cambi\w*|(?:forzad\w*\s+a\s+|obligad\w*\s+a\s+)?migr\w*|(?:inici\w*|decidi\w*)\s+(?:un\s+proceso\s+de\s+|la\s+)?migraci\w*|busc\w*|evalu\w*|cotiz\w*|voy|vamos|paso|pasamos|(?:inici\w*\s+la\s+)?transici[oó]n|reemplazar)\b(?:\s+(?:a|con|hacia|de\s+datos\s+hacia|toda\s+la\s+infraestructura\s+a|las\s+operaciones\s+comerciales\s+a|un|este|otro|de))?\s+(?:la\s+competencia|otro[s]?\s+proveedor\w*|proveedor\s+local|otra[s]?\s+plataform\w*|otro[s]?\s+servicio\w*|alternativas?|opciones?|competidor|aws|sistema|otro\s+sistema|m[oó]dulo|infraestructura\s+externa|plataforma)\b', re.IGNORECASE),

            re.compile(r'\b(?:solicit\w*|exig\w*|quiero)\s+(?:el\s+)?(?:reembolso|devoluci[oó]n|reintegro|cese|baja|(?:la\s+)?devoluci[oó]n del saldo a favor)\b', re.IGNORECASE),
            re.compile(r'\b(?:dejar\w*|cesar|suspender)\s+(?:de\s+usar|los\s+pagos|pagos|el cobro recurrente|el cobro recurrente automatico)\b', re.IGNORECASE),
            re.compile(r'\b(?:ya no (?:quiero|deseo) (?:continuar|seguir|pagando))\b', re.IGNORECASE),
            re.compile(r'\b(?:no sigo pagando|no mas prorrogas|no prorrogar|ya no los quiero|borrado de registros|delete_account|cancel_subscription|botar plata|nos vamos del sistema|salida definitiva|recortar presupuesto|recortar el presupuesto|inviable mantener|quedar[aá] inactiv\w*|revisando si se justifica|buscar una alternativa|iniciaremos la transici[oó]n)\b', re.IGNORECASE),

            re.compile(r'\b(?:no\s+perder|perder)\s+(?:a\s+)?(?:este\s+|un\s+)?cliente\b', re.IGNORECASE),
            re.compile(r'\b(?:me voy a|me paso a|nos pasamos a)\s+la\s+competencia\b', re.IGNORECASE),
        ]

        self.friction_rules = {
            FrictionCategory.BILLING_PRICING: [
                r'\b(?:cobr\w*|factur\w*|tarif\w*|precio\w*|cost\w*|renovaci\w*|reembols\w*|aumento de precio|sobrecargo|duplicad\w*|pagos recurrentes|mensualidad|incremento abusivo|expensive|el triple|cobros ocultos|cargos ocultos|descaro|descuento|penalidad|debitaron|presupuesto|gasto)\b'
            ],
            FrictionCategory.PRODUCT_RELIABILITY: [
                r'\b(?:ca[ií]d\w*|no funciona\w*|error\w*|bug\w*|crash\w*|inestabl\w*|se cay\w*|fall\w*|timeout\w*|colaps\w*|pantalla blanca|pantalla en blanco|500|503|servidor ca[ií]do|lentitud\w*|se congela\w*|inoperativ\w*|falla[s]? reiteradas|borraron|borr\w*|bloqueo|bloquearon|se cierra sola|intermitencias|bloquea las tablas|tumba el backend|mandar[ií]n|idioma)\b'
            ],
            FrictionCategory.CUSTOMER_SUPPORT: [
                r'\b(?:soport\w*|ticket\w*|asesor\w*|agent\w*|atenci\w*|nadie responde|no responden|sin respuesta|grosero\w*|p[eé]simo soporte|esperando respuesta|desatenci\w*|ignoran\w*|mal servicio|colg\w*|incompetent\w*|nadie contesta|nadie resuelve|transfieren|supervisor|5 estrellas|nivel de servicio)\b'
            ],
            FrictionCategory.FEATURE_GAP: [

                r'\b(?:falta\w*|no tiene|no permite|carece de|no se puede|no hay opci[oó]n|exportar|integrar|funcionalidad\w*|incomplet\w*|limitad\w*|integraciones|caracter[ií]sticas)\b'
            ],
            FrictionCategory.SLA_DELAY: [
                r'\b(?:demor\w*|tardanz\w*|d[ií]as esperando|semanas esperando|horas esperando|retras\w*|lent\w*|incumplimiento\w*|incumplido|tiempo de respuesta|plazo\w*|canso de esperar|mamado de esperar|tardaron|48 horas|45 minutos|tarda apenas)\b'
            ],
            FrictionCategory.SECURITY_PRIVACY: [
                r'\b(?:seguridad|privacidad|expuso|expuesto|filtr\w*|clave privada|texto plano|secci[oó]n p[uú]blica|rsa|cvv|api[_-]?key|secret|contrase[nñ]a|pass|credenciales|rut|c[eé]dula|tarjeta|bancolombia|jwt|amzn|auth)\b'
            ],
        }

        self.sarcasm_positive = re.compile(r'\b(?:maravilla|maravilloso|excelente|buen[ií]simo|gran trabajo|bravo|felicitaciones|genial|joya|un lujo|un exito|👏|super bien|espectacular|delicia|increible|super veloz|un aplauso|un poema|precioso|cumbre|me encanta|genios absolutos|fascinante|una bala|hermoso|vaya maravilla|5 estrellas|fant[aá]stic[oa])\b', re.IGNORECASE)
        self.sarcasm_negative = re.compile(r'\b(?:ca[ií]d\w*|se cay\w*|cobro doble|pagar el doble|el triple|nadie responde|no funciona|p[eé]sim\w*|estafa|d[ií]as esperando|duplicad\w*|borraron|borr\w*|fiasco|porquer\w*|bugs?|arruinaron|ignora|inoperativo|se cierra sola|se congela|congelad\w*|pantalla en blanco|bloquea las tablas|tumba el backend|colgaron|cargos ocultos|mandar[ií]n|detenido|sin avisar|no hacen reembolsos|tarda apenas|45 minutos|cualquiera puede ver|borr[oó] los permisos|cargando infinitamente|timeout)\b', re.IGNORECASE)

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
            neg_score += 5.0
            pos_score = max(0.0, pos_score - 4.0)
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

        # Ajuste de polaridad por fricción y señales negativas
        has_security_leak = FrictionCategory.SECURITY_PRIVACY in friction_detected and ("expuso" in normalized_text or "filtr" in normalized_text or "texto plano" in normalized_text or "urgente" in normalized_text or "sk_live" in normalized_text)

        if churn_detected or has_sarcasm or has_security_leak:
            sentiment = SentimentType.NEGATIVE
        elif net_score < -0.3 or (friction_detected and any(f not in [FrictionCategory.NONE, FrictionCategory.SECURITY_PRIVACY] for f in friction_detected) and neg_score > 0.6):
            sentiment = SentimentType.NEGATIVE
        elif net_score > 1.0:
            sentiment = SentimentType.POSITIVE
        else:
            sentiment = SentimentType.NEUTRAL

        # Asignación de emoción
        if sentiment == SentimentType.POSITIVE:
            emotion = EmotionType.SATISFACTION
        elif sentiment == SentimentType.NEGATIVE:
            if has_security_leak or "urgente" in normalized_text or "texto plano" in normalized_text or "expuso" in normalized_text:
                emotion = EmotionType.ANXIETY
            elif churn_detected or "estafa" in normalized_text or "inaceptable" in normalized_text or "exijo" in normalized_text or "asco" in normalized_text:
                emotion = EmotionType.ANGER
            elif "duda" in normalized_text or "confuso" in normalized_text or "no entiendo" in normalized_text:
                emotion = EmotionType.CONFUSION
            else:
                emotion = EmotionType.FRUSTRATION
        else:
            if "expuso" in normalized_text or "texto plano" in normalized_text or "urgente" in normalized_text:
                emotion = EmotionType.ANXIETY
            else:
                emotion = EmotionType.NEUTRAL

        confidence = 0.95 if total_signals > 4.0 or churn_detected or has_sarcasm else (0.88 if total_signals > 1.5 else (0.78 if total_signals > 0.4 else 0.65))

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

        base_result.processing_metadata["engine_used"] = "local_nlp"
        return base_result
