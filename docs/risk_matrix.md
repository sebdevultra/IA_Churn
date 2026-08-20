# Matriz de Gestión de Riesgos Técnicos y Operacionales

A continuación se detalla la matriz de análisis y mitigación de riesgos del sistema **ChurnGuard AI**:

| ID | Riesgo Identificado | Probabilidad | Impacto | Nivel de Riesgo | Estrategia de Mitigación Implementada |
|---|---|---|---|---|---|
| **R-01** | **Latencia elevada en llamadas a IA** | Media | Medio | **MODERADO** | Implementación de timeouts estrictos (15s), uso de modelos ligeros optimizados (*gpt-4o-mini*), procesamiento asíncrono en segundo plano mediante scheduler y provider local de respuesta ultrarrápida. |
| **R-02** | **Sobrecosto por explosión de tokens** | Alta | Alto | **ALTO** | Estrategia de `ContextManagerService`: envío de resumen histórico condensado (<150 tokens) en lugar de historiales completos, limitando el costo promedio por interacción a menos de \$0.0001 USD. |
| **R-03** | **Alucinaciones de IA en cálculo numérico de Churn** | Alta | Crítico | **CRÍTICO** | Desacoplamiento estricto: la IA **nunca** calcula porcentajes ni scores. La IA únicamente extrae señales cualitativas (sentimiento, emoción, intención booleana); Python calcula el score mediante fórmulas matemáticas determinísticas. |
| **R-04** | **Caída o indisponibilidad del proveedor de IA (503/429)** | Media | Alto | **ALTO** | Persistencia inmediata de la interacción en estado `PENDING_AI_ANALYSIS` antes de invocar la IA, política de 3 reintentos con backoff exponencial y job periódico de recuperación. Ninguna interacción se pierde. |
| **R-05** | **JSON malformado o corrupto devuelto por el LLM** | Media | Medio | **MODERADO** | Mecanismo de saneamiento heurístico `_sanitize_and_repair_json` (extracción regex, eliminación de bloques markdown) complementado con validación estricta en esquemas Pydantic. |
| **R-06** | **Caída de la Base de Datos Relacional** | Baja | Crítico | **ALTO** | *Healthcheck* activo en `/api/v1/health`, transacciones atómicas con *rollback* automático en `SessionLocal` y configuración de *pool pre-ping* para reconexión transparente. |
| **R-07** | **Ingesta de interacciones duplicadas** | Alta | Medio | **MODERADO** | Generación determinística de fingerprint SHA-256 (`DeduplicationService`) indexado con constraint `UNIQUE` en base de datos. Descarte idempotente con log de auditoría. |
| **R-08** | **Payloads incompletos o mensajes vacíos** | Media | Bajo | **BAJO** | Validadores de campo en Pydantic (`min_length=1`, eliminación de whitespace) que rechazan solicitudes vacías con código HTTP 422 *Unprocessable Entity*. |
| **R-09** | **Falsos positivos (Alertas críticas injustificadas)** | Media | Medio | **MODERADO** | Exigencia de combinaciones ponderadas: para alcanzar CRITICAL ($\ge 80$), se requiere intención explícita de cancelación sumada a frustración/soporte o recurrencia histórica. Ajuste por nivel de confianza. |
| **R-10** | **Falsos negativos (Churn inminente no detectado)** | Baja | Alto | **ALTO** | Análisis de múltiples dimensiones semánticas (emociones, quejas de soporte, fallas de fiabilidad, quejas de facturación y multiplicador Enterprise del 1.1x). |
| **R-11** | **Fallo o solapamiento en ejecución de APScheduler** | Baja | Medio | **BAJO** | Concurrencia protegida mediante `_worker_lock` (mutualmente excluyente) y `max_instances=1`, impidiendo carreras de ejecución si una tarea previa aún sigue en curso. |

---

## Criterios de Monitoreo de Riesgos

1. **Tasa de error de Pipeline**: Si supera el 5%, se dispara alerta en logs y el endpoint `/health` reporta estado degradado.
2. **Alertas no reconocidas**: Panel en el Dashboard con contador visual y filtro de alertas en estado `NEW` para evitar cuellos de botella humanos.
3. **Control de Duplicados**: Métrica acumulativa visible en tiempo real en el pie del Dashboard.
