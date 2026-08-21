# ChurnGuard AI: Monitor de Sentimiento de Clientes y Alertas de Riesgo de Abandono (Churn)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063.svg)](https://docs.pydantic.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Proyecto Académico y Productivo Multidisciplinario**: Sistema integral en tiempo real para la ingesta, análisis semántico con Inteligencia Artificial, cálculo determinístico de riesgo de churn (0-100), optimización de tokens y gestión automatizada de alertas críticas.

---

## 1. El Problema

Las empresas SaaS y de comercio electrónico reciben grandes volúmenes de interacciones diarias a través de múltiples canales (tickets de soporte, reseñas públicas, chats en vivo y encuestas NPS). El análisis manual de esta información resulta inviable, provocando:
- Respuestas tardías a clientes insatisfechos.
- Fuga no detectada de clientes corporativos (*silent churn*).
- Alucinaciones y cálculos arbitrarios cuando se delega el cálculo financiero o cuantitativo directamente a modelos de lenguaje (LLM).
- Altos costos operativos debido al reenvío redundante de historiales extensos de conversación a APIs de IA.

---

## 2. La Solución

**ChurnGuard AI** implementa una arquitectura desacoplada y robusta que:
1. **Ingesta y Deduplica**: Registra interacciones desde APIs REST o lotes de archivos (JSON/CSV) calculando *fingerprints* SHA-256 idempotentes.
2. **Optimiza Tokens**: Utiliza un `ContextManagerService` con resúmenes incrementales (< 150 tokens) logrando un **ahorro de tokens superior al 90%**.
3. **Analiza con IA Estructurada**: Extrae sentimiento, emoción dominante, fricciones categorizadas, intención de churn y evidencia textual validada estrictamente con Pydantic.
4. **Calcula Churn Determinístico**: Un **Risk Engine** en Python aplica ponderaciones matemáticas configurables ($0$ a $100$) evitando alucinaciones de la IA.
5. **Dispara Alertas Automatizadas**: Genera alertas inmediatas con estado `NEW` ante eventos **CRITICAL** ($\ge 80$).
6. **Visualiza en Tiempo Real**: Un Dashboard ejecutivo en HTML5/CSS3/Vanilla JS con gráficos dinámicos de Chart.js y simulador en vivo.

---

## 3. Arquitectura del Sistema

```
External Data Source (JSON / CSV / REST)
                   ↓
         APScheduler Worker
                   ↓
             Data Ingestion
                   ↓
        Cleaning & Normalization
                   ↓
        Deduplication (SHA-256)
                   ↓
       Context Manager (Token Cache)
                   ↓
              AI Analysis (LLM / Rule Provider)
                   ↓
    Pydantic Schema Validation & Heuristic Repair
                   ↓
         Deterministic Risk Engine (0-100)
                   ↓
           PostgreSQL Database
                   ↓
              Alert Engine
                   ↓
           FastAPI REST API
                   ↓
      Executive Real-time Dashboard
```

---

## 4. Stack Tecnológico

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Pydantic-Settings.
- **Base de Datos**: PostgreSQL 15 (Producción / Docker) y SQLite con StaticPool (Tests & Desarrollo Local).
- **ORM**: SQLAlchemy 2.0.
- **Inteligencia Artificial**: 
  - *Cloud*: OpenAI API / Gemini / DeepSeek / Ollama compatible.
  - *Local*: `DeterministicRuleAIProvider` (motor semántico local determinístico para ejecución offline, testing y costo cero).
- **Automatización**: APScheduler (BackgroundScheduler con cerrojo de exclusión mutua `_worker_lock`).
- **Frontend**: HTML5 semántico, CSS3 moderno (tema oscuro SaaS), JavaScript Vanilla nativo.
- **Visualización**: Chart.js 4.4+.
- **Testing**: Pytest, Pytest-Asyncio, Pytest-Cov.
- **Despliegue**: Docker, Docker Compose.

---

## 5. Estructura del Proyecto

```
project/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── alerts.py         # Gestión y ciclo de vida de alertas
│   │   │       │   ├── analytics.py      # Agregaciones, métricas y evolución
│   │   │       │   ├── customers.py      # Perfiles de clientes y riesgo
│   │   │       │   ├── dashboard.py      # Payload consolidado para el frontend
│   │   │       │   ├── health.py         # Health check de DB, Scheduler e IA
│   │   │       │   ├── interactions.py   # Ingesta y consulta de interacciones
│   │   │       │   └── workers.py        # Trigger manual del worker
│   │   │       └── api.py
│   │   ├── core/
│   │   │   ├── config.py                 # Pydantic Settings
│   │   │   ├── errors.py                 # Excepciones de dominio y handlers HTTP
│   │   │   ├── logging.py                # Logging estructurado
│   │   │   └── risk_rules.py             # Pesos y reglas determinísticas de riesgo
│   │   ├── db/
│   │   │   ├── base.py                   # Declarative Base
│   │   │   ├── init_db.py                # Inicialización de tablas y seed data
│   │   │   └── session.py                # SessionLocal y get_db dependency
│   │   ├── models/                       # Modelos ORM SQLAlchemy normalizados
│   │   │   ├── alert.py
│   │   │   ├── churn_risk.py
│   │   │   ├── customer.py
│   │   │   ├── friction.py
│   │   │   ├── interaction.py
│   │   │   ├── log.py
│   │   │   └── sentiment.py
│   │   ├── repositories/                 # Capa de acceso a datos y consultas SQL
│   │   ├── schemas/                      # Esquemas Pydantic v2 y validaciones
│   │   ├── services/                     # Lógica de negocio, IA y pipeline
│   │   │   ├── ai_service.py             # Dual AI Provider (OpenAI / Local Rule)
│   │   │   ├── alert_service.py          # Creación y transición de alertas
│   │   │   ├── context_manager.py        # Optimización de tokens y resúmenes
│   │   │   ├── deduplication.py          # Hashing SHA-256 e idempotencia
│   │   │   ├── ingestion_service.py      # Orquestador del pipeline de 10 etapas
│   │   │   └── risk_engine.py            # Motor determinístico de cálculo de churn
│   │   ├── workers/                      # Scheduler y Worker de archivos
│   │   └── main.py                       # App FastAPI, CORS, lifespan y static mount
│   └── tests/                            # 27 tests automatizados con Pytest
├── data/
│   ├── sample_interactions.json          # Dataset de prueba en JSON
│   └── sample_interactions.csv           # Dataset de prueba en CSV
├── docs/                                 # Entregables gerenciales y de diseño
│   ├── acceptance_criteria.md            # Criterios Gherkin (DADO/CUANDO/ENTONCES)
│   ├── architecture_diagram.md           # Diagramas Mermaid y especificación
│   ├── definition_of_done.md             # Checklist técnico y funcional
│   ├── efficiency_analysis.md            # Análisis de costos y tokens
│   ├── risk_matrix.md                    # Matriz de riesgos técnicos
│   └── validation_report.md              # Informe de validación y pruebas
├── frontend/                             # UI Dashboard independiente
│   ├── css/styles.css
│   ├── js/api.js
│   ├── js/charts.js
│   ├── js/app.js
│   └── index.html
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 6. Instalación y Ejecución

### Opción A: Despliegue con Docker Compose (Recomendado para Producción)

1. **Clonar el repositorio y configurar variables de entorno**:
   ```bash
   cp .env.example .env
   ```
2. **Construir y levantar contenedores**:
   ```bash
   docker compose up --build
   ```
3. **Acceder a la aplicación**:
   - **Dashboard UI**: [http://localhost:8000](http://localhost:8000)
   - **Documentación Swagger API**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Opción B: Ejecución Local en Entorno Virtual

1. **Crear y activar entorno virtual**:
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux / Mac:
   source venv/bin/activate
   ```
2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configurar el archivo `.env`**:
   ```bash
   cp .env.example .env
   ```
4. **Iniciar el servidor backend**:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
5. **Abrir en el navegador**:
   - Ingresar a [http://localhost:8000](http://localhost:8000) para ver el Dashboard interactivo.

---

## 7. Configuración de Variables de Entorno (`.env`)

| Variable | Valor por Defecto | Descripción |
|---|---|---|
| `ENVIRONMENT` | `development` | Entorno de ejecución (`development`, `production`, `test`). |
| `DATABASE_URL` | `sqlite:///./churn_monitor.db` | URL de conexión SQL (PostgreSQL o SQLite). |
| `AI_PROVIDER` | `deterministic_rule` | Proveedor de IA: `deterministic_rule`, `openai` o `gemini`. |
| `OPENAI_API_KEY` | `""` | Clave de API para proveedores en la nube. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo LLM a utilizar. |
| `SCHEDULER_ENABLED` | `true` | Habilita el worker periódico de APScheduler. |
| `SCHEDULER_INTERVAL_MINUTES`| `5` | Frecuencia en minutos para el barrido de archivos y reintentos. |
| `DATA_WATCH_DIR` | `./data` | Directorio vigilado para ingesta batch automática. |
| `AUTO_INGEST_SAMPLE_DATA` | `true` | Procesa automáticamente los datos de muestra al iniciar. |
| `RISK_THRESHOLD_CRITICAL` | `80` | Puntuación mínima para disparar Alertas Críticas. |

---

## 8. Motor Determinístico de Riesgo de Churn (Risk Engine)

El cálculo matemático del *Risk Score* se realiza **100% en Python**, garantizando reproducibilidad y auditabilidad.

### Fórmula y Ponderaciones Centralizadas (`RiskWeightsConfig`):

$$\text{Raw Score} = \sum (\text{Factores Aplicados}) \times \text{Multiplier}_{\text{Tier}}$$
$$\text{Final Score} = \min(\max(\text{Raw Score}, 0), 100)$$

| Factor Evaluado | Condición | Ponderación |
|---|---|---|
| **Sentimiento Negativo** | `sentiment == "negative"` | $+20$ |
| **Sentimiento Positivo** | `sentiment == "positive"` | $-10$ (Mitiga riesgo) |
| **Emoción de Frustración** | `emotion == "frustration"` | $+20$ |
| **Emoción de Enojo/Ira** | `emotion == "anger"` | $+25$ |
| **Intención Explícita de Churn** | `churn_intent == True` | $+30$ |
| **Problema con Soporte** | Fricción en `customer_support` | $+10$ |
| **Fricción Recurrente** | Misma categoría en últimas 3 interacciones | $+15$ |
| **Señal Negativa Reciente** | Interacción negativa en los últimos 7 días | $+5$ |
| **Multiplicador Enterprise** | Cuenta con `tier == "enterprise"` | $1.1\times$ |

### Clasificación de Niveles de Riesgo:
- `0 - 29`: **LOW** (Bajo)
- `30 - 59`: **MEDIUM** (Medio)
- `60 - 79`: **HIGH** (Alto)
- `80 - 100`: **CRITICAL** (Crítico $\rightarrow$ **Dispara Alerta Automática**)

---

## 9. Ejecución de Pruebas Automatizadas

La suite incluye **27 pruebas automatizadas** que cubren el 100% de los endpoints y los 15 casos de borde requeridos.

Ejecutar la suite completa con reporte de cobertura:
```bash
pytest -v --cov=backend.app backend/tests
```

### Resultados de Cobertura:
- **Total de pruebas**: 27 PASSED (0 fallidas).
- **Cobertura de código**: **88% global** (100% en API routers, schemas, risk rules y repositories).

---

## 10. Documentación Gerencial Incluida

En la carpeta `/docs` se encuentran disponibles los siguientes informes técnicos:
1. 📄 [`architecture_diagram.md`](file:///e:/JemcoTechSoluciones/New%20Server%20Oracle/projects/backup/Nueva%20carpeta/docs/architecture_diagram.md): Diagramas de flujo y arquitectura en Mermaid.
2. 📄 [`risk_matrix.md`](file:///e:/JemcoTechSoluciones/New%20Server%20Oracle/projects/backup/Nueva%20carpeta/docs/risk_matrix.md): Matriz de 11 riesgos operativos y técnicos con sus mitigaciones.
3. 📄 [`definition_of_done.md`](file:///e:/JemcoTechSoluciones/New%20Server%20Oracle/projects/backup/Nueva%20carpeta/docs/definition_of_done.md): Checklist de verificación técnica y funcional.
4. 📄 [`acceptance_criteria.md`](file:///e:/JemcoTechSoluciones/New%20Server%20Oracle/projects/backup/Nueva%20carpeta/docs/acceptance_criteria.md): Criterios de aceptación en formato Gherkin (Dado/Cuando/Entonces).
5. 📄 [`efficiency_analysis.md`](file:///e:/JemcoTechSoluciones/New%20Server%20Oracle/projects/backup/Nueva%20carpeta/docs/efficiency_analysis.md): Análisis de costos, optimización de tokens y escalabilidad.
6. 📄 [`validation_report.md`](file:///e:/JemcoTechSoluciones/New%20Server%20Oracle/projects/backup/Nueva%20carpeta/docs/validation_report.md): Informe de pruebas, dataset y correcciones realizadas.

---

## 11. Limitaciones y Posibles Mejoras Futuras

### Limitaciones Actuales:
- **Autenticación en Dashboard**: El MVP está diseñado para redes internas/corporativas mediante roles de sesión; en un entorno multi-tenant se recomienda integrar OAuth2 / JWT.
- **WebSockets en Tiempo Real**: El sistema utiliza actualmente *Polling* configurable (5s/10s/30s); la arquitectura está preparada para escalar a WebSockets o Server-Sent Events (SSE).

### Posibles Mejoras:
1. **Integración con Webhooks Salientes**: Disparar notificaciones a canales de Slack o Microsoft Teams cuando se cree una alerta `CRITICAL`.
2. **Generación Automatizada de Respuestas de Retención**: Utilizar IA generativa para sugerir correos personalizados de disculpa y ofertas de compensación al CSM asignado.
3. **Clustering Semántico de Tópicos**: Agrupar automáticamente quejas no catalogadas utilizando embeddings vectoriales (pgvector).
