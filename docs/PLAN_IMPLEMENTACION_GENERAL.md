# 🌐 Plan Maestro de Implementación General
**Proyecto 6 — Monitor de Sentimiento de Clientes y Alertas de Riesgo de Abandono (Churn)**

*Documento de arquitectura integral y coordinación técnica del Sprint de 3 días para el equipo de desarrollo.*

---

## 🎯 1. Visión General del Proyecto

### 1.1 El Problema de Negocio
Las empresas reciben volúmenes masivos de feedback no estructurado (tickets de soporte, reseñas públicas, encuestas NPS/CSAT y chats). Los métodos tradicionales basados en palabras clave fallan ante el sarcasmo, las quejas sutiles y la falta de categorización de causa raíz, impidiendo intervenir a tiempo antes de que los clientes de alto valor abandonen el servicio (*Churn*).

### 1.2 La Solución de Ingeniería
Un sistema analítico automatizado de alta resiliencia compuesto por:
1. **Pipeline de Ingesta & IA (Inferencia en Cascada de 3 Niveles):** Sanitización PII exhaustiva (10 entidades), Nivel 1 Simbólico (<1ms), Nivel 2 Transformer Neuronal Local (~20ms) y Nivel 3 Cloud LLM (Gemini) para casos críticos Enterprise.
2. **Core Backend & Risk Engine:** Base de datos relacional (6 tablas normalizadas), motor de riesgo determinista (0–100 pts), gestión transaccional de alertas y API RESTful.
3. **Dashboard Analítico en Tiempo Real:** Visualización interactiva con Chart.js, KPIs de salud, tabla de casos críticos y simulador de feedback en vivo.

---

## 👥 2. Las 3 Rutas de Trabajo del Equipo

```mermaid
graph TD
    subgraph FUENTES [1. Fuentes de Ingesta Externa]
        F1[Tickets de Soporte]
        F2[Reseñas Web / Redes]
        F3[Encuestas CSAT / NPS]
    end

    subgraph RUTA_2 [Ruta 2: AI & Data Pipeline Architect - 3 Niveles]
        FUENTES --> P1[Limpieza & PII Scrubbing 10 Entidades]
        P1 --> P2[Nivel 1: Motor Simbólico / Léxico <1ms]
        P2 --> P3{¿Caso Obvio / Positivo?}
        P3 -- "SÍ (~60%)" --> P6[Salida JSON Estructurada]
        P3 -- "NO" --> P4[Nivel 2: Transformer Neuronal Local TNL PyTorch ~20ms]
        P4 --> P5{¿Caso Crítico / Enterprise?}
        P5 -- "NO (~35%)" --> P6
        P5 -- "SÍ (~5%)" --> P7[Nivel 3: Cloud Gemini LLM Deep Analysis]
        P7 --> P6
        P6 --> P8[Scheduler de Ingesta Idempotente]
    end

    subgraph RUTA_1 [Ruta 1: Backend & Core Engineer]
        P8 --> B1[(Base de Datos Relacional: 6 Tablas)]
        B1 --> B2[Modelos Pydantic & Repositorio CRUD]
        B2 --> B3[Risk Engine: Cálculo Determinista 0-100 pts]
        B3 --> B4[Sistema Transaccional de Alertas]
        B4 --> B5[API REST FastAPI con OpenAPI]
    end

    subgraph RUTA_3 [Ruta 3: Frontend & Integration Lead]
        B5 <--> C1[Dashboard Analítico Web Reactivo]
        C1 --> C2[Gráficos Chart.js: Tendencia 30d & Fricciones]
        C1 --> C3[Consola de Intervención: Casos Críticos & Badges]
        C1 --> C4[Simulador / Testbed en Vivo]
        C1 --> C5[Sondeo Polling Periódico cada 5s]
    end
```

---

### 🛠️ RUTA 1: Backend & Core Engineer
* **Documento Detallado:** [`docs/PLAN_IMPLEMENTACION_BACKEND_CORE.md`](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/PLAN_IMPLEMENTACION_BACKEND_CORE.md)
* **Entregables Clave:**
  1. **Esquema Relacional de 6 Tablas:** `customers`, `interactions`, `sentiment_analysis`, `friction_points`, `churn_risk`, `alerts`.
  2. **Risk Engine Determinista (0–100 pts):** Sentimiento negativo ($+20$), Frustración ($+20$), Intención explícita de cancelar ($+30$), Recurrencia ($+15$), Soporte/SLA ($+10$), Señal reciente ($+5$).
  3. **Sistema de Alertas Transaccional:** Disparo en niveles `Alto` (60–79) y `Crítico` (80–100) con estados (`PENDING`, `IN_REVIEW`, `RESOLVED`) y prevención de duplicados/cooldown.
  4. **API FastAPI:** Endpoints documentados en OpenAPI para ingesta, analítica, gestión de alertas y health check.

---

### 🧠 RUTA 2: AI & Data Pipeline Architect
* **Documento Detallado:** [`docs/PLAN_IMPLEMENTACION_AI_DATA_PIPELINE.md`](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/PLAN_IMPLEMENTACION_AI_DATA_PIPELINE.md)
* **Entregables Clave:**
  1. **Sanitización & PII Scrubbing:** Enmascaramiento de 10 entidades sensibles (emails, teléfonos, cédulas, tarjetas, cuentas bancarias, IPs, contraseñas, direcciones, nombres).
  2. **Inferencia en Cascada de 3 Niveles:** 
     - *Nivel 1 (Simbólico <1ms):* Resuelve casos obvios y positivos a costo \$0 y 0 MB RAM (~60% tráfico).
     - *Nivel 2 (Transformer Neuronal Local ~20ms):* Procesa quejas y clasifica fricciones con red neuronal en PyTorch (~35% tráfico).
     - *Nivel 3 (Cloud Gemini LLM ~1500ms):* Escalado exclusivo para el 5% de casos críticos Enterprise.
  3. **Contrato JSON Estructurado:** Entrega estricta de `{ sentiment, emotion, friction_points, churn_intent, confidence, evidence }`.
  4. **Worker de Ingesta con Scheduler:** Automatización periódica con APScheduler, control de idempotencia y reintentos.

---

### 🎨 RUTA 3: Frontend & Integration Lead
* **Documento Detallado:** [`docs/PLAN_IMPLEMENTACION_FRONTEND_INTEGRATION.md`](file:///c:/Users/SEBAS/Desktop/Antigravit/HU_seman4_IA/docs/PLAN_IMPLEMENTACION_FRONTEND_INTEGRATION.md)
* **Entregables Clave:**
  1. **Tablero Analítico Reactivo:** KPIs superiores (Total procesados, % Sentimiento neto, NPS predictivo, Casos críticos).
  2. **Visualizaciones Chart.js:** Gráfico de evolución temporal de sentimiento a 30 días y gráfico de barras de puntos de fricción.
  3. **Matriz de Intervención:** Tabla dinámica de clientes en riesgo con badges de severidad, evidencia textual y modal de resolución rápida.
  4. **Testbed / Simulador en Vivo:** Consola para inyectar feedback en vivo y visualizar la respuesta inmediata de la IA y el Risk Engine.
  5. **Sincronización:** Sondeo periódico inteligente (*polling* cada 5s) con manejo de estados de carga y error.

---

## 🏛️ 3. Principio Arquitectónico Rector

> [!IMPORTANT]
> **Separación de Responsabilidades:** La IA interpreta lenguaje y extrae señales semánticas estructuradas; el Backend valida y aplica las reglas de negocio deterministas. Los cálculos matemáticos de riesgo, los umbrales de alerta, la persistencia y la deduplicación no dependen jamás de texto libre generado por el LLM.

---

## 📚 4. Estructura de Entregables del Proyecto

```text
HU_seman4_IA/
├── docs/
│   ├── PLAN_IMPLEMENTACION_GENERAL.md               # Plan Maestro General
│   ├── PLAN_IMPLEMENTACION_BACKEND_CORE.md          # Especificación para Backend
│   ├── PLAN_IMPLEMENTACION_AI_DATA_PIPELINE.md      # Especificación para AI Architect
│   ├── PLAN_IMPLEMENTACION_FRONTEND_INTEGRATION.md  # Especificación para Frontend Lead
│   ├── 01_DIAGRAMA_ARQUITECTURA_SOLUCION.md         # Entregable Gerencial 1
│   ├── 02_MATRIZ_RIESGOS_Y_MITIGACION.md            # Entregable Gerencial 2
│   ├── 03_DEFINICION_DE_HECHO_Y_CRITERIOS_ACEPTACION.md # Entregable Gerencial 3
│   ├── 04_ANALISIS_EFICIENCIA_Y_ELECCION_TECNOLOGICA.md # Entregable Gerencial 4
│   └── 05_INFORME_VALIDACION_Y_METRICAS_IMPACTO.md  # Entregable Gerencial 5
├── ai_pipeline/                                     # Módulos del AI Architect
├── backend/                                         # Módulos del Backend Engineer
├── static/                                          # Interfaz Web del Frontend Lead
└── tests/                                           # Suite completa de pruebas
```
