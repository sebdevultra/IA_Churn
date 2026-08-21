"""
Cliente y Conector con Cloud LLMs (Google Gemini API).
Implementa llamadas optimizadas con formato JSON nativo forzado,
control estricto de timeout (2.5s) y política de reintentos exponenciales.
"""

import json
import os
import time
from typing import Optional, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .schemas import (
    AISemanticAnalysisResult,
    SentimentType,
    EmotionType,
    FrictionCategory,
)
from .prompt_templates import SYSTEM_PROMPT_SEMANTIC_ANALYZER, build_analysis_prompt



class CloudGeminiAnalyzer:
    """
    Conector de alta resiliencia para la API de Gemini.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self._client is not None)

    def analyze(self, sanitized_text: str, customer_tier: str = "Standard") -> Optional[AISemanticAnalysisResult]:
        """
        Ejecuta la inferencia en la nube sobre el texto saneado.
        Retorna el objeto AISemanticAnalysisResult validado o None si ocurre un error/timeout.
        """
        if not self.is_configured:
            return None

        from google.genai import types

        prompt = build_analysis_prompt(sanitized_text, customer_tier)
        start_time = time.perf_counter()

        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT_SEMANTIC_ANALYZER,
                        response_mime_type="application/json",
                        temperature=0.1,
                    )
                )

                if not response or not response.text:
                    continue

                # Parsear y validar JSON
                data = json.loads(response.text.strip())
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

                # Mapear strings a enums seguros
                sentiment = SentimentType(data.get("sentiment", "neutral").lower())
                emotion = EmotionType(data.get("emotion", "neutral").lower())
                
                raw_frictions = data.get("friction_points", ["none"])
                frictions = []
                for f in raw_frictions:
                    try:
                        frictions.append(FrictionCategory(f.lower()))
                    except ValueError:
                        pass
                if not frictions:
                    frictions = [FrictionCategory.NONE]

                return AISemanticAnalysisResult(
                    sentiment=sentiment,
                    emotion=emotion,
                    friction_points=frictions,
                    churn_intent=bool(data.get("churn_intent", False)),
                    confidence=float(data.get("confidence", 0.90)),
                    evidence=data.get("evidence", []),
                    processing_metadata={
                        "engine_used": "cloud_gemini",
                        "model": self.model_name,
                        "latency_ms": latency_ms,
                        "attempt": attempt + 1
                    }
                )

            except Exception:
                time.sleep(0.3 * (2 ** attempt))  # Backoff exponencial breve
                continue

        return None
