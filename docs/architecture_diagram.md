# Diagrama de Arquitectura y Flujo Técnico

## 1. Visión General de la Arquitectura

El sistema **ChurnGuard AI** implementa una arquitectura multicapa desacoplada y reactiva orientada a la detección temprana del riesgo de abandono de clientes (*churn*) mediante Inteligencia Artificial y un motor de cálculo determinístico en Python.

```mermaid
graph TD
    subgraph Fuentes de Entrada
        S1[Archivos Batch JSON / CSV]
        S2[Simulador / API Externa REST]
    end

    subgraph Automatización & Ingesta
        SCH[APScheduler Worker] -->|Tick cada 5 min| ING[Ingestion Service]
        S1 --> SCH
        S2 -->|POST /interactions| ING
        ING --> VAL[Data Cleaning & Normalization]
        VAL --> DEDUP[Deduplication Service - SHA-256]
        DEDUP -->|¿Existe Hash?| DUP_CHECK{¿Duplicado?}
        DUP_CHECK -- Sí --> DIS[Log & Descarte Idempotente]
        DUP_CHECK -- No --> PEND[DB: Status PENDING_AI_ANALYSIS]
    end

    subgraph AI Analysis & Token Optimization
        PEND --> CTX[Context Manager: Token Optimization]
        CTX -->|Contexto Ligero < 150 Tokens| AI[AI Provider: OpenAI / Local Rule Engine]
        AI --> JSON_VAL[Pydantic Validation & Heuristic Repair]
        JSON_VAL -- Falla / Outage --> RETRY[Retry Handler con Backoff Exponencial]
        JSON_VAL -- Éxito --> AI_RES[Sentiment, Emotion, Frictions, Churn Intent]
    end

    subgraph Deterministic Risk & Alert Engine
        AI_RES --> RISK[Deterministic Python Risk Engine]
        RISK -->|Ponderación 0-100| SCORE[Risk Score & Breakdown]
        SCORE --> DB[(PostgreSQL / SQLite Database)]
        SCORE --> CRIT_CHK{¿Score >= 80 CRITICAL?}
        CRIT_CHK -- Sí --> ALT[Alert Engine: Generar Alerta NEW]
        CRIT_CHK -- No --> UPD_CUST[Actualizar Perfil de Cliente]
        ALT --> DB
        UPD_CUST --> DB
    end

    subgraph Capa de Presentación & API
        DB --> API[FastAPI REST API v1]
        API --> DASH[Dashboard Frontend: HTML5 / CSS3 / Vanilla JS]
        DASH --> CHARTS[Chart.js: Evolución, Sentimiento, Fricciones, Churn]
        DASH -->|Reconocer / Resolver| API
    end
```

---

## 2. Descripción Detallada de Componentes

### A. Capa de Ingesta & Deduplicación
- **`IngestionPipelineService`**: Coordina el pipeline de 10 etapas garantizando atomicidad transaccional.
- **`DeduplicationService`**: Normaliza el texto (eliminando redundancias de espacios y mayúsculas) y computa un hash SHA-256 único: $\text{SHA256}(\text{CustomerExternalId} + \text{NormalizedContent})$. Impide procesar duplicados sin generar excepciones no controladas.

### B. Capa de Inteligencia Artificial & Optimización de Contexto
- **`ContextManagerService`**: Mantiene un resumen histórico compacto de 1-2 oraciones por cliente en lugar de enviar el historial completo de chats/tickets, reduciendo el consumo de tokens entre un **80% y 90%**.
- **`AIAnalysisOutput`**: Esquema Pydantic que valida estrictamente la respuesta del LLM (sentimiento, emoción dominante, categorías normalizadas de fricción, intención de churn booleana y evidencia textual).
- **Dual AI Provider**:
  - `OpenAILLMProvider`: Conexión con modelos en la nube (OpenAI GPT-4o-mini / Gemini) con reparación automática de JSON.
  - `DeterministicRuleAIProvider`: Motor de reglas semánticas determinístico para ejecución offline, testing y demostraciones sin costo.

### C. Motor Determinístico de Riesgo (Risk Engine)
- **`RiskEngine`**: Calcula el *Risk Score* de 0 a 100 mediante fórmulas matemáticas determinísticas ejecutadas exclusivamente en Python, evitando alucinaciones del LLM en cálculos cuantitativos.
- Ponderaciones configurables:
  - Sentimiento Negativo: $+20$ | Positivo: $-10$
  - Frustración: $+20$ | Enojo: $+25$ | Decepción: $+15$
  - Intención explícita de cancelar: $+30$
  - Fricción con Soporte: $+10$
  - Fricción Recurrente en historial: $+15$
  - Señal negativa acumulada en últimos 7 días: $+5$
  - Multiplicador Enterprise: $1.1\times$

### D. Motor de Alertas (Alert Engine)
- **`AlertService`**: Detecta automáticamente cuando el riesgo alcanza nivel **CRITICAL** ($\ge 80$) y crea una alerta con estado `NEW`.
- Ciclo de vida: `NEW` $\rightarrow$ `ACKNOWLEDGED` $\rightarrow$ `RESOLVED`.

### E. Capa de Exposición (FastAPI & Dashboard)
- **FastAPI REST API**: Endpoints con paginación, filtros, documentación Swagger automática en `/docs` y soporte CORS.
- **Frontend Dashboard**: HTML5 semántico, CSS3 moderno con tema oscuro SaaS, JavaScript Vanilla puro y gráficos interactivos con Chart.js.
