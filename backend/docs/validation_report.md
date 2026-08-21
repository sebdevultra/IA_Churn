# Informe de Validación y Resultados de Pruebas

## 1. Resumen Ejecutivo de Validación

El sistema **ChurnGuard AI** fue sometido a una batería completa de pruebas unitarias, de integración, de resiliencia y de casos de borde (*edge cases*) utilizando **Pytest** y **FastAPI TestClient** con base de datos aislada en memoria.

| Métrica de Validación | Resultado Obtenido | Estado |
|---|---|---|
| **Total de Tests Automatizados** | 20 pruebas | **100% PASS** |
| **Tasa de Éxito de Pipeline** | 100.0% | **CUMPLIDO** |
| **Tiempo de Ejecución de Suite** | < 2.5 segundos | **ÓPTIMO** |
| **Idempotencia / Deduplicación** | 100% de colisiones detectadas y bloqueadas | **CUMPLIDO** |
| **Resiliencia ante Caídas de IA** | 0% pérdida de datos (estado `PENDING_AI_ANALYSIS`) | **CUMPLIDO** |
| **Ponderación Determinística de Riesgo** | Exactitud matemática de $0$ a $100$ | **CUMPLIDO** |

---

## 2. Dataset Utilizado para Pruebas

Se diseñaron dos conjuntos de datos representativos en la carpeta `/data`:

1. **`data/sample_interactions.json`**:
   - 10 interacciones completas con metadata de clientes Enterprise, Pro y Standard.
   - Casos cubiertos: Quejas de soporte prolongadas, caídas de API en producción, fallas de facturación, felicitaciones de clientes satisfechos, feedback ambiguo NPS y cancelaciones explícitas.
2. **`data/sample_interactions.csv`**:
   - 5 interacciones estructuradas en formato tabular para validar la ingesta batch de fuentes externas legadas.

---

## 3. Matriz de Cobertura de los 15 Casos Críticos

| # | Caso de Prueba | Entrada de Prueba | Comportamiento Esperado | Resultado |
|---|---|---|---|---|
| **1** | **Mensaje Positivo** | *"Excelente servicio, estoy muy satisfecho."* | `sentiment=positive`, `risk=LOW` ($Score \le 29$) | **PASÓ** |
| **2** | **Mensaje Negativo** | *"Estoy harto de esperar días para recibir soporte."* | `sentiment=negative`, `emotion=frustration`, $Score \ge 50$ | **PASÓ** |
| **3** | **Frustración Marcada** | *"Es inaceptable y una vergüenza."* | `emotion=anger/frustration`, peso extra asignado | **PASÓ** |
| **4** | **Intención de Cancelar** | *"Si esto continúa voy a cancelar mi suscripción."* | `churn_intent=true`, $Score \ge 80$ (`CRITICAL`) | **PASÓ** |
| **5** | **Mensaje Ambiguo** | *"Bueno... esperaba algo diferente."* | `sentiment=neutral`, $Score < 60$ (No crítico) | **PASÓ** |
| **6** | **Mensaje Vacío** | `""` o espacios en blanco `"   "` | Rechazado con código HTTP `422 Unprocessable Entity` | **PASÓ** |
| **7** | **Datos Incompletos** | Payload sin `customer_external_id` | Rechazado por Pydantic con código `422` | **PASÓ** |
| **8** | **Duplicados** | Misma interacción enviada 2 veces | Primera procesada (`201`), segunda rechazada (`409 Conflict`) | **PASÓ** |
| **9** | **IA Caída / Timeout** | Excepción `503 Service Unavailable` | Interacción persiste con `PENDING_AI_ANALYSIS` | **PASÓ** |
| **10** | **JSON Inválido de IA** | Respuesta envuelta en markdown ` ```json ... ``` ` | Reparación heurística exitosa sin fallar | **PASÓ** |
| **11** | **Historial Largo** | Cliente con 10+ interacciones previas | Context Manager comprime contexto a $<150$ tokens | **PASÓ** |
| **12** | **Alerta Crítica** | $Score \ge 80$ | Inserción automática de alerta con estado `NEW` | **PASÓ** |
| **13** | **Actualización Alerta** | `PATCH /alerts/{id}` | Transición `NEW` $\rightarrow$ `ACKNOWLEDGED` $\rightarrow$ `RESOLVED` | **PASÓ** |
| **14** | **Reprocesamiento / Retries** | Función `retry_pending_interactions()` | Reintento exitoso y estado `PROCESSED` | **PASÓ** |
| **15** | **Concurrencia de Scheduler** | Intentos de ejecución simultánea | Bloqueo por `_worker_lock` sin colisión | **PASÓ** |

---

## 4. Hallazgos, Errores Encontrados y Correcciones Realizadas

1. **Dependencia `email-validator` en Pydantic**:
   - *Hallazgo*: El validador `EmailStr` en Pydantic 2 requería el paquete opcional `email-validator`.
   - *Corrección*: Se agregó `email-validator>=2.1.0` a `requirements.txt` y se instaló en el entorno de ejecución.
2. **Sanitización de JSON con bloques Markdown de LLM**:
   - *Hallazgo*: Algunos modelos LLM devuelven JSON rodeado de backticks ` ```json ... ``` `.
   - *Corrección*: Se implementó la función `_sanitize_and_repair_json` con expresiones regulares para extraer limpiamente el objeto JSON antes de pasarlo a Pydantic.
3. **Control de duplicados sin interrupción del worker batch**:
   - *Hallazgo*: El worker batch de CSV/JSON se detenía al encontrar el primer duplicado.
   - *Corrección*: Se envolvió cada elemento en un bloque `try-except DuplicateInteractionError` que incrementa el contador de duplicados y continúa procesando los registros restantes de manera segura.
