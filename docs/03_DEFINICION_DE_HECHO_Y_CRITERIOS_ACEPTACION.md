# ✅ Documento Ejecutivo 3: Definición de Hecho (DoD) y Criterios de Aceptación
**Proyecto 6 — Monitor de Sentimiento de Clientes y Alertas de Riesgo de Abandono (Churn)**

---

## 🎯 1. Propósito del Documento

Este documento establece el marco riguroso de calidad técnica y funcional que certifica que el sistema cumple con los estándares de ingeniería para ser promovido a un entorno de producción (Production Readiness).

---

## 📋 2. Definición de Hecho (Definition of Done - DoD)

Un incremento o módulo del sistema se considera **HECHO (DONE)** únicamente cuando cumple con el siguiente checklist técnico transversal:

### ⚙️ 2.1 Calidad de Código & Arquitectura
- [x] **Separación de Capas:** Código modular desacoplado entre Ingesta/IA (`ai_pipeline/`), Persistencia/Negocio (`backend/`) e Interfaz (`static/`).
- [x] **Arquitectura de Inferencia en 3 Niveles:** Nivel 1 (Léxico <1ms), Nivel 2 (TNL PyTorch ~20ms) y Nivel 3 (Cloud LLM ~1500ms).
- [x] **Tipado Estricto:** 100% de los modelos y contratos de datos definidos con Pydantic v2 y type hints de Python.
- [x] **Principio de Separación:** Ningún cálculo determinista (Score de Churn, alertas) depende de texto libre generado por LLM.

### 🧪 2.2 Cobertura de Pruebas & Calidad
- [x] **Suite de Pruebas Automatizadas:** 100% de los 12 casos de prueba obligatorios implementados y pasando con `pytest`.
- [x] **Pruebas de Casos de Borde (Edge Cases):** Textos vacíos, payloads gigantes (+2000 chars), caracteres no imprimibles y datos sensibles (PII).
- [x] **Pruebas de Resiliencia:** Validación del switch automático a Local NLP ante caídas simuladas de Cloud LLM.

### 🛡️ 2.3 Seguridad, Privacidad & Resiliencia
- [x] **PII Scrubbing Activo (10 Entidades):** Enmascaramiento comprobado de emails, teléfonos, cédulas, tarjetas de crédito, cuentas bancarias, IPs, credenciales, direcciones y nombres.
- [x] **Idempotencia:** Bloqueo de duplicados en la ingesta por identificador único de interacción.
- [x] **Tolerancia a Fallos:** Manejo de excepciones por registro individual sin detener el worker de ingesta.

### 📚 2.4 Documentación & Contratos
- [x] **5 Documentos Ejecutivos Completados:** Arquitectura, Riesgos, DoD, Justificación Tecnológica e Informe de Validación.
- [x] **Planes de Trabajo Específicos:** Guías técnicas para Backend, AI Architect y Frontend en `docs/`.

---

## 🔍 3. Criterios de Aceptación por Componente

### 🧠 3.1 Pipeline de IA & Datos (`ai_pipeline/`)
| Criterio | Validación | Estado |
|---|---|:---:|
| **Sanitización PII** | 10 entidades sensibles se sustituyen por su respectivo tag `[TAG_MASKED]` | ✅ Aprobado |
| **Contrato Estructurado** | La salida cumple estrictamente con el schema `{ sentiment, emotion, friction_points, churn_intent, confidence, evidence }` | ✅ Aprobado |
| **Inferencia en 3 Niveles** | Casos positivos se resuelven en N1 (<1ms), quejas complejas en N2 (~20ms) y casos críticos en N3 | ✅ Aprobado |
| **Fallback Transparente** | Si no hay API key o hay error 503, el sistema entrega respuesta válida con motor local | ✅ Aprobado |
| **Sarcasmo / Ironía** | Detecta contradicciones semánticas y clasifica como negativo con frustración | ✅ Aprobado |

### 🛠️ 3.2 Backend & Risk Engine (`backend/`)
| Criterio | Validación | Estado |
|---|---|:---:|
| **Esquema Relacional** | 6 tablas normalizadas con claves primarias y foráneas (`customers`, `interactions`, etc.) | ✅ Aprobado |
| **Fórmula de Churn** | Cálculo matemático exacto de puntos (+20, +20, +30, +15, +10, +5) acotado en $[0, 100]$ | ✅ Aprobado |
| **Generación de Alertas** | Scores $\ge 60$ generan alertas con severidad `HIGH` o `CRITICAL` y estado `PENDING` | ✅ Aprobado |
| **API REST FastAPI** | Endpoints documentados en OpenAPI con respuestas JSON válidas | ✅ Aprobado |

### 🎨 3.3 Dashboard & Integración (`static/`)
| Criterio | Validación | Estado |
|---|---|:---:|
| **KPIs en Tiempo Real** | Visualización clara de volumen procesado, sentimiento neto, NPS y casos críticos | ✅ Aprobado |
| **Gráficos Dinámicos** | Chart.js renderiza evolución temporal a 30 días y distribución de fricciones | ✅ Aprobado |
| **Consola de Intervención** | Tabla de casos de alto riesgo con badge de severidad y acción de resolución | ✅ Aprobado |
| **Simulador en Vivo** | Permite inyectar texto y ver el resultado instantáneo del análisis semántico | ✅ Aprobado |
