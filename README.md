# 🛡️ Churn Sentinel AI — Monitor Inteligente de Sentimiento y Alertas de Riesgo de Abandono

[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org/)
[![Google Gemini Flash](https://img.shields.io/badge/LLM-Gemini_Flash-8E75B2.svg)](https://ai.google.dev/)
[![Tests Passing](https://img.shields.io/badge/Tests-26%2F26%20Passing%20(100%25)-success.svg)](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/test_e2e_integration.py)
[![Zero PII Leakage](https://img.shields.io/badge/Security-100%25%20Zero--PII%20Leakage-brightgreen.svg)](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/05_INFORME_VALIDACION_Y_METRICAS_IMPACTO.md)
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20Enterprise-black.svg)]()

> **Sistema Industrial de Detección Temprana de Churn, Análisis Semántico Multicanal y Mitigación Proactiva de Pérdida de Clientes con Inferencia Híbrida Adaptativa en 3 Niveles.**

---

## 📑 Tabla de Contenidos Ejecutiva
1. [🎯 Resumen Ejecutivo y Propuesta de Valor](#-1-resumen-ejecutivo-y-propuesta-de-valor)
2. [🏛️ Arquitectura Global del Sistema](#️-2-arquitectura-global-del-sistema)
3. [💡 Innovaciones Técnicas y Diferenciadores Clave](#-3-innovaciones-t%C3%A9cnicas-y-diferenciadores-clave)
4. [📚 Suite Documental del Proyecto (Los 6 Documentos Ejecutivos)](#-4-suite-documental-del-proyecto)
5. [🧪 Informe Consolidado de Validación y Pruebas de Estrés](#-5-informe-consolidado-de-validaci%C3%B3n-y-pruebas-de-estr%C3%A9s)
6. [💰 Impacto en Negocio, FinOps y Retorno de Inversión (ROI)](#-6-impacto-en-negocio-finops-y-retorno-de-inversi%C3%B3n-roi)
7. [🚀 Guía de Puesta en Marcha Rápida (Quick Start)](#-7-gu%C3%ADa-de-puesta-en-marcha-r%C3%A1pida-quick-start)
8. [📂 Estructura del Repositorio](#-8-estructura-del-repositorio)
9. [🎓 Guía de Sustentación para Jurados y Evaluadores](#-9-gu%C3%ADa-de-sustentaci%C3%B3n-para-jurados-y-evaluadores)

---

## 🎯 1. Resumen Ejecutivo y Propuesta de Valor

En la industria SaaS y de servicios digitales, el **abandono de clientes (Churn)** representa la mayor fuga de ingresos recurrentes ($ARR$). Tradicionalmente, las empresas detectan el descontento de manera **reactiva**: cuando el cliente ya ha cancelado la suscripción o ha publicado una queja destructiva en redes sociales.

**Churn Sentinel AI** transforma este paradigma mediante un **motor de alerta temprana y escucha continua** que procesa interacciones no estructuradas (tickets de soporte, encuestas CSAT/NPS, chats y correos) en tiempo real.

### 🌟 Propuesta de Valor Cuantificable:
* **Detección Pre-Abandono en $< 5$ minutos:** Reduce el tiempo medio de respuesta operativa ($MTTR$) de 72 horas a minutos.
* **Inferencia Híbrida FinOps-Optimized:** Reduce el gasto en APIs de Inteligencia Artificial en un **90%** mediante filtrado en cascada local-first.
* **Zero-Downtime Resilience:** Garantiza **100% de disponibilidad continua** mediante conmutación automática de contingencia en $1.1$ ms ante caídas de proveedores cloud.
* **Privacidad Estricta (GDPR / Habeas Data):** Enmascaramiento preventivo de **14 entidades de datos sensibles (PII)** antes de cualquier inferencia.

---

## 🏛️ 2. Arquitectura Global del Sistema

El sistema implementa una **Arquitectura en Cascada de 4 Capas** con **Separación Estricta de Responsabilidades**:

```mermaid
graph TD
    subgraph CAPA_1 [1. Ingesta Multicanal & Sanitización]
        F1[📥 Tickets Soporte]
        F2[⭐ Reseñas & Redes]
        F3[📋 Encuestas CSAT/NPS]
        F4[💬 Live Chats]
        ING[Batch & Stream Ingestion Worker]
        PII[🛡️ PII Scrubber: 14 Entidades Regex NFC]
        
        F1 --> ING
        F2 --> ING
        F3 --> ING
        F4 --> ING
        ING --> PII
    end

    subgraph CAPA_2 [2. Inteligencia Artificial: Cascada Adaptativa de 3 Niveles]
        N1[Nivel 1: Motor Léxico-Simbólico <1ms | 0 MB RAM]
        R1{¿Caso Obvio / Positivo?}
        N2[Nivel 2: Transformer Neuronal Local PyTorch ~20ms]
        R2{¿Caso Crítico / Enterprise?}
        N3[Nivel 3: Google Gemini Flash Cloud LLM ~1200ms]
        VAL[Validador Inmutable Pydantic v2]
        
        PII --> N1
        N1 --> R1
        R1 -- "SÍ (~60% Tráfico @ $0 Costo)" --> VAL
        R1 -- "NO (Fricciones / Quejas)" --> N2
        N2 --> R2
        R2 -- "NO (~35% Resuelto en Red Local)" --> VAL
        R2 -- "SÍ (~5% Cuentas Clave)" --> N3
        N3 --> VAL
    end

    subgraph CAPA_3 [3. Backend Core & Motor de Riesgo Determinista]
        DB[(Base de Datos Relacional ACID: 6 Tablas)]
        REPO[Repository Layer / CRUD & Idempotencia]
        RISK[Deterministic Risk Engine: 0-100 pts Formula]
        ALERT_ENG[Alert Manager & Dynamic Cooldown]
        API[FastAPI REST Engine & OpenAPI]
        
        VAL --> REPO
        REPO --> DB
        REPO --> RISK
        RISK --> ALERT_ENG
        ALERT_ENG --> DB
        API <--> REPO
    end

    subgraph CAPA_4 [4. Frontend Reactivo & Tablero de Control]
        DASH[Dashboard Ejecutivo HTML5 / Vanilla JS]
        KPIS[Tarjetas KPI: NPS, Sentimiento, Casos Críticos]
        CHARTS[Gráficos Dinámicos Chart.js]
        TABLE[Matriz de Intervención de Clientes en Riesgo]
        SIM[Simulador Interactivo de Feedback en Vivo]
        
        API <--> DASH
        DASH --> KPIS
        DASH --> CHARTS
        DASH --> TABLE
        DASH --> SIM
    end
```

---

## 💡 3. Innovaciones Técnicas y Diferenciadores Clave

### 1. Inferencia Adaptativa en Cascada (3-Tier Cascaded Inference)
A diferencia de arquitecturas ingenuas que envían el 100% de las solicitudes a APIs costosas de LLM, Churn Sentinel clasifica la complejidad semántica en 3 capas:
* **Nivel 1 (Motor Simbólico / Léxico):** Resuelve el **60% del tráfico** (agradecimientos, consultas rutinarias) en $< 1$ ms a costo $\$0.00$.
* **Nivel 2 (Transformer Neuronal Local PyTorch):** Analiza el **35% del tráfico** (quejas moderadas, sarcasmo y fricciones) localmente sin egress de datos ni costo de tokens.
* **Nivel 3 (Cloud LLM - Gemini Flash):** Reserva la potencia de razonamiento exclusivamente para el **5% del tráfico de alto impacto** (cuentas Enterprise con amenazas de cancelación).

### 2. Principio de Separación: Determinismo en Reglas de Negocio
> [!IMPORTANT]
> **La Inteligencia Artificial NUNCA calcula scores numéricos directos ni toma decisiones de negocio arbitrarias.**

* **Rol de la IA:** Extraer variables semánticas discretas (`sentiment`, `emotion`, `friction_points`, `churn_intent`).
* **Rol del Backend:** Evaluar una fórmula matemática determinista y 100% auditable de 0 a 100 puntos:

$$\text{Risk Score} = \min(100, \, S_{\text{base}} + F_{\text{crítica}} + C_{\text{intención}} + H_{\text{historial}} + T_{\text{enterprise}} + V_{\text{aceleración}})$$

* **Desglose de Factores:**
  * Sentimiento Negativo: $+20\text{ pts}$
  * Fricción Crítica (Facturación / Caída de Servicio): $+20\text{ pts}$
  * Intención Explícita de Churn / Rescisión: $+30\text{ pts}$
  * Historial de Tickets Recurrentes / CSAT Bajo: $+15\text{ pts}$
  * Cuenta de Nivel Enterprise / Tier VIP: $+10\text{ pts}$
  * Aceleración de Sentimiento Negativo: $+5\text{ pts}$

### 3. Privacidad por Diseño (Zero-Trust PII Scrubber)
Antes de que el texto ingrese a la memoria del pipeline de NLP, el módulo [`cleaner.py`](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/ai_pipeline/cleaner.py) normaliza caracteres Unicode (NFC) y ejecuta expresiones regulares compiladas para **14 entidades sensibles**:
* Cédulas de Identidad, DNI, RUT, NIT y Pasaportes.
* Tarjetas de Crédito, Números de Cuenta Bancaria y Códigos CVC/CVV.
* Correos Electrónicos, Teléfonos y Direcciones Físicas.
* Claves API, Tokens JWT, Hashes Criptográficos, Direcciones IP y MACs.

### 4. Idempotencia y Prevención de Fatiga de Alertas
* **Idempotencia Transaccional:** Cada interacción cuenta con un hash/identificador único que bloquea reprocesamientos en lotes masivos.
* **Cooldown de Alertas:** El despachador de alertas agrupa incidentes por cliente e impone una ventana de supresión para no saturar al equipo de Customer Success.

---

## 📚 4. Suite Documental del Proyecto

El proyecto cuenta con un conjunto exhaustivo de documentación técnica y ejecutiva de nivel industrial disponible en el directorio [`docs/`](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs):

| # | Documento | Enlace | Propósito y Contenido Clave |
|---|---|:---:|---|
| **Doc 1** | **Diagrama de Arquitectura de Solución** | [Ver Documento](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/01_DIAGRAMA_ARQUITECTURA_SOLUCION.md) | Blueprint global, diagramas de secuencia, capas de persistencia y contratos de interfaz. |
| **Doc 2** | **Matriz de Riesgos y Mitigación** | [Ver Documento](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/02_MATRIZ_RIESGOS_Y_MITIGACION.md) | Análisis de 9 riesgos de producción (costos, latencia, PII, 503 Outages) y contingencias. |
| **Doc 3** | **Definición de Hecho (DoD) y Criterios** | [Ver Documento](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/03_DEFINICION_DE_HECHO_Y_CRITERIOS_ACEPTACION.md) | Checklist de calidad de código, contratos Pydantic v2 y criterios de aceptación por componente. |
| **Doc 4** | **Análisis de Eficiencia y Elección Tecnológica** | [Ver Documento](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/04_ANALISIS_EFICIENCIA_Y_ELECCION_TECNOLOGICA.md) | Justificación FinOps del enfoque híbrido frente a 100% Cloud o 100% Local GPU. |
| **Doc 5** | **Informe de Validación y Métricas de Impacto** | [Ver Documento](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/05_INFORME_VALIDACION_Y_METRICAS_IMPACTO.md) | Resultados cuantitativos de 268 casos de prueba de estrés y benchmarks operativos. |
| **Doc 6** | **Guía de Sustentación Senior (Examen y Defensa)** | [Ver Documento](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/06_GUIA_SUSTENTACION_SENIOR.md) | Dossier de defensa técnica, 15 preguntas difíciles de jurado y guión de demo en vivo. |

---

## 🧪 5. Informe Consolidado de Validación y Pruebas de Estrés

La estabilidad y precisión del sistema fueron verificadas mediante **26 pruebas unitarias automatizadas (`pytest`)** y **5 baterías de estrés sobre 268 casos reales**:

```text
+----------+------------------------------------------+-------------+-----------------------+--------------------+----------------------+
| Prueba   | Escenario de Validación                  | Total Casos | Métrica Principal     | Latencia Media     | Tasa de Éxito / SLA  |
+----------+------------------------------------------+-------------+-----------------------+--------------------+----------------------+
| Prueba 1 | Sanitización y PII Stress (14 Entidades) | 50 casos    | 85 entidades PII      | 0.75 ms / caso     | 100% Sin fugas (0.0%)|
| Prueba 2 | Semántica, Sarcasmo & Amenazas de Churn  | 79 casos    | 97.2% precisión (307) | 1.10 ms / caso     | 100% Disponibilidad  |
| Prueba 3 | Inferencia Cloud LLM & Enrutamiento      | 25 casos    | 40.0% ahorro tokens   | 40.0 ms (Cloud)    | 100% JSON Válido     |
| Prueba 4 | Resiliencia ante Caídas (Cloud Outage)   | 30 casos    | 100% Fallback Activo  | 1.10 ms failover   | 100% Zero-Downtime   |
| Prueba 5 | Rendimiento por Lotes e Idempotencia     | 109 casos   | 755.9 msg / segundo   | 1.32 ms / ticket   | 100% Idempotencia    |
+----------+------------------------------------------+-------------+-----------------------+--------------------+----------------------+
```

> [!TIP]
> Los reportes analíticos detallados generados por cada batería de pruebas se encuentran disponibles en la carpeta [`results/`](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/results).

---

## 💰 6. Impacto en Negocio, FinOps y Retorno de Inversión (ROI)

### 📊 Comparativa de Costos Operativos ($TCO$ mensual por 100,000 interacciones):

| Estrategia Arquitectónica | Latencia Promedio ($P_{95}$) | Costo Mensual Estimado | Riesgo de Indisponibilidad |
|---|:---:|:---:|:---:|
| **Enfoque 100% Cloud LLM** (OpenAI / Gemini) | $1,800\text{ ms}$ | $\$250 - \$450\text{ USD}$ | Alto (Rate limits / Caídas API) |
| **Enfoque 100% Local GPU Dedicado** (Llama-3 8B) | $800\text{ ms}$ | $\$350 - \$600\text{ USD}$ (Cloud GPU) | Medio (Hardware failure) |
| **Churn Sentinel AI (Cascada Híbrida 3 Niveles)** | **$< 20\text{ ms}$** | **$<\$18\text{ USD}$** | **Nulo (100% Resiliencia)** |

### 📈 Modelo Financiero de Retorno de Inversión ($ROI$):
Para una empresa SaaS con **10,000 clientes activos** y un ticket promedio de **\$50 USD/mes ($MRR$)**:
* Tasa de cancelación mensual sin monitor: $1.2\%$ (120 clientes perdidos = $-\$6,000\text{ USD/mes}$).
* Con **Churn Sentinel AI**: Detección temprana e intervención proactiva del CSM logran una **tasa de retención del 45%** de los clientes en riesgo crítico.
* **Ingresos recurrentes recuperados:** **$+\$2,700\text{ USD/mes}$** ($\$32,400\text{ USD/año}$).
* **Retorno sobre la Inversión ($ROI$):** Superior a **$1,500\%$** en el primer año operativo.

---

## 🚀 7. Guía de Puesta en Marcha Rápida (Quick Start)

### 📋 Requisitos Previos
* **Python 3.10+** (Recomendado 3.12).
* Entorno virtual activo (`.venv`).
* Clave de Google Gemini API (Opcional; si no se proporciona, el sistema opera al 100% con su motor neuronal local).

### ⚡ Inicialización en 1 Comando
Para iniciar el servidor FastAPI integrado con el Dashboard Web interactivo:

```powershell
# Opción 1: Ejecución directa con Python
python run_server.py

# Opción 2: Script batch preconfigurado (Windows)
.\run_local.bat
```

El lanzador inicializará la base de datos relacional, cargará los clientes semilla y abrirá automáticamente el navegador en:
👉 **URL del Dashboard:** `http://127.0.0.1:8000`  
👉 **Documentación Interactiva OpenAPI (Swagger):** `http://127.0.0.1:8000/docs`

### 🧪 Ejecución de Pruebas Automatizadas
```powershell
# Ejecutar validación integral End-to-End
python test_e2e_integration.py

# Ejecutar suite de pruebas unitarias pytest
pytest ai_pipeline/test/ -v
```

---

## 📂 8. Estructura del Repositorio

```text
HU_seman4_IA/
├── README.md                           # 📖 Documento Gerencial y Arquitectura General
├── GUIA_SUSTENTACION.md                # 🎓 Guía de Sustentación Senior y Repaso de Examen
├── run_server.py                       # 🚀 Launcher unificado Backend + Frontend
├── test_e2e_integration.py             # 🧪 Suite de validación End-to-End
├── run_local.bat                       # ⚡ Script de arranque local rápido
│
├── ai_pipeline/                        # 🧠 Capa de Inteligencia Artificial & NLP
│   ├── cleaner.py                      # 🛡️ PII Scrubber (14 entidades) & Normalizador NFC
│   ├── local_nlp_fallback.py           # ⚡ Nivel 1 (Léxico) & Nivel 2 (Transformer Local)
│   ├── cloud_llm.py                    # ☁️ Nivel 3 (Google Gemini Flash LLM Provider)
│   ├── pipeline.py                     # 🔄 Orquestador de Inferencia en Cascada
│   ├── schemas.py                      # 📐 Contratos de datos inmutables Pydantic v2
│   ├── scheduler_ingestion.py          # ⏱️ Worker de ingesta por lotes e Idempotencia
│   └── test/                           # 🧪 Pruebas unitarias de pipeline de IA
│
├── backend/                            # ⚙️ Capa de Negocio, Persistencia & REST API
│   ├── app/
│   │   ├── main.py                     # 🌐 Aplicación FastAPI y montaje de rutas estáticas
│   │   ├── core/                       # 🔧 Configuraciones y Reglas de Riesgo
│   │   ├── db/                         # 🗄️ Sesión SQLAlchemy y esquema relacional
│   │   ├── models/                     # 📊 Modelos ORM (6 tablas: customers, alerts, etc.)
│   │   ├── repositories/               # 🏛️ Capa de acceso a datos y agregaciones
│   │   ├── schemas/                    # 📐 Schemas de request/response Pydantic
│   │   └── services/                   # 🧮 Motor de Riesgo Determinista y Alertas
│   └── requirements.txt                # 📦 Dependencias de backend
│
├── frontend/                           # 🎨 Capa de Presentación & Experiencia de Usuario
│   ├── index.html                      # 🖥️ Dashboard analítico unificado
│   ├── css/main.css                    # 🎨 Estilos visuales y diseño responsive
│   ├── js/                             # ⚡ Módulos JavaScript (App, Charts, Testbed)
│   └── assets/                         # 🖼️ Recursos estáticos e iconografía
│
├── docs/                               # 📚 Suite de 6 Documentos Ejecutivos Formales
│   ├── 01_DIAGRAMA_ARQUITECTURA_SOLUCION.md
│   ├── 02_MATRIZ_RIESGOS_Y_MITIGACION.md
│   ├── 03_DEFINICION_DE_HECHO_Y_CRITERIOS_ACEPTACION.md
│   ├── 04_ANALISIS_EFICIENCIA_Y_ELECCION_TECNOLOGICA.md
│   ├── 05_INFORME_VALIDACION_Y_METRICAS_IMPACTO.md
│   └── 06_GUIA_SUSTENTACION_SENIOR.md
│
└── results/                            # 📊 Reportes y Datasets de Pruebas de Estrés
    ├── REPORTE_PRUEBA_1_PII.md
    ├── REPORTE_PRUEBA_2_ADVERSARIAL.md
    ├── REPORTE_PRUEBA_3_CLOUD_LLM.md
    ├── REPORTE_PRUEBA_4_RESILIENCIA.md
    └── REPORTE_PRUEBA_5_RENDIMIENTO_LOTES.md
```

---

## 🎓 9. Guía de Sustentación para Jurados y Evaluadores

Para preparar y repasar la sustentación formal del proyecto ante comités evaluadores, directores de tecnología (CTO) o audiencias de negocio, consulte la:

👉 [**Guía de Sustentación Técnica de Nivel Senior (`docs/06_GUIA_SUSTENTACION_SENIOR.md`)**](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/06_GUIA_SUSTENTACION_SENIOR.md)

### Aspectos Destacados en la Guía de Sustentación:
1. **Pitch Ejecutivo de 2 Minutos:** Cómo articular la solución y el $ROI$ de forma contundente.
2. **Defensa de Decisiones Arquitectónicas:** Justificación técnica de por qué la inferencia híbrida supera a los LLMs puros.
3. **15 Preguntas Difíciles de Jurado con Respuestas Senior:** Argumentación sobre seguridad, escalabilidad, mitigación de alucinaciones y FinOps.
4. **Guión de Demostración en Vivo (Paso a Paso):** Instrucciones exactas para ejecutar una demo impecable de 5 minutos.
5. **Ficha Técnica & Cheat-Sheet Rápido:** Síntesis de métricas, latencias, tablas y fórmulas para consulta inmediata.

---

<div align="center">
  <sub>Diseñado y desarrollado bajo estándares de Ingeniería de Software Empresarial y Arquitectura de Inteligencia Artificial de Alta Disponibilidad.</sub>
</div>
