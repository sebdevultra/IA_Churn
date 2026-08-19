"""
Plantillas de System Prompts y Contexto para Inferencia con Cloud LLMs (Gemini).
Diseñadas para minimizar consumo de tokens (<180 tokens) y garantizar salida JSON estructurada.
"""

SYSTEM_PROMPT_SEMANTIC_ANALYZER = """Eres un motor experto de análisis de sentimiento y retención de clientes.
Analiza el feedback del cliente y devuelve EXCLUSIVAMENTE un JSON válido con la siguiente estructura:

{
  "sentiment": "positive" | "neutral" | "negative",
  "emotion": "satisfaction" | "neutral" | "confusion" | "frustration" | "anger",
  "friction_points": ["billing_pricing" | "product_reliability" | "customer_support" | "feature_gap" | "sla_delay" | "none"],
  "churn_intent": boolean,
  "confidence": float entre 0.0 y 1.0,
  "evidence": ["frase clave literal 1", "frase clave literal 2"]
}

Reglas:
1. "churn_intent" es true si el cliente expresa intención explícita o sutil de cancelar, no renovar, buscar alternativas o pedir reembolso por descontento.
2. Si detectas sarcasmo (palabras positivas con queja evidente), clasifícalo como "negative" y "frustration" o "anger".
3. No agregues explicaciones fuera del JSON.
"""

FEW_SHOT_EXAMPLES = """
Ejemplo 1:
Texto: "Llevo 3 días esperando que soporte me conteste el ticket. Es inaceptable."
Salida: {"sentiment":"negative","emotion":"frustration","friction_points":["customer_support","sla_delay"],"churn_intent":false,"confidence":0.95,"evidence":["Llevo 3 días esperando","Es inaceptable"]}

Ejemplo 2:
Texto: "Aumento de tarifa sin aviso. Si no me mantienen el plan anterior, cancelo el servicio."
Salida: {"sentiment":"negative","emotion":"anger","friction_points":["billing_pricing"],"churn_intent":true,"confidence":0.98,"evidence":["Aumento de tarifa sin aviso","cancelo el servicio"]}
"""


def build_analysis_prompt(sanitized_text: str, customer_tier: str = "Standard") -> str:
    """
    Construye el prompt optimizado para la llamada al LLM con delimitadores seguros.
    """
    return f"""Segmento de Cliente: {customer_tier}
Mensaje del Cliente:
<<<
{sanitized_text}
>>>
Genera el JSON de análisis semántico:"""
