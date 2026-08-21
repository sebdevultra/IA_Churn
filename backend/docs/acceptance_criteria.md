# Criterios de Aceptación (Gherkin Format)

A continuación se formalizan los criterios de aceptación en formato **DADO / CUANDO / ENTONCES** para cada componente del sistema:

---

## 1. Ingesta y Validación de Datos

### Escenario 1.1: Ingesta de interacción válida
- **DADO** que el sistema recibe una solicitud `POST /api/v1/interactions` con un payload válido que incluye `customer_external_id`, `source_type` y `content`.
- **CUANDO** el pipeline valida y procesa la interacción.
- **ENTONCES** la interacción se persiste con estado `PROCESSED`, se calcula su sentimiento y riesgo de churn, y la API responde con código `201 Created` y los datos completos de la interacción.

### Escenario 1.2: Rechazo de mensaje vacío
- **DADO** que un usuario o sistema externo envía una interacción con `content` vacío o que solo contiene espacios en blanco.
- **CUANDO** la solicitud es evaluada por la capa de esquemas.
- **ENTONCES** la solicitud es rechazada inmediatamente con código HTTP `422 Unprocessable Entity` y no se persiste ningún registro en base de datos.

---

## 2. Deduplicación e Idempotencia

### Escenario 2.1: Detección y rechazo de interacción idéntica
- **DADO** que una interacción con texto "X" para el cliente "CUST-1001" ya fue procesada y almacenada previamente.
- **CUANDO** se envía nuevamente la misma interacción con idéntico cliente y texto.
- **ENTONCES** el servicio `DeduplicationService` detecta la colisión de hash SHA-256, la API responde con código `409 Conflict`, se registra el intento en los logs de auditoría y no se duplica el cálculo de riesgo.

---

## 3. Inteligencia Artificial y Estructura de Salida

### Escenario 3.1: Extracción semántica y validación Pydantic
- **DADO** un mensaje de feedback como: *"Estoy harto de esperar días para recibir soporte. Es una vergüenza."*
- **CUANDO** la interacción pasa por el servicio de análisis de IA.
- **ENTONCES** el modelo devuelve un JSON estructurado con `sentiment = "negative"`, `emotion = "frustration"`, `friction_points` con categoría `customer_support`, `confidence >= 0.90` y citas textuales en `evidence`.

### Escenario 3.2: Manejo de respuesta con bloques markdown de código
- **DADO** que el proveedor LLM devuelve el JSON envuelto en etiquetas ```json ... ```.
- **CUANDO** se ejecuta la función `_sanitize_and_repair_json`.
- **ENTONCES** las etiquetas markdown son removidas limpiamente, el JSON es parseado exitosamente y validado por Pydantic sin lanzar errores.

---

## 4. Cálculo Determinístico de Riesgo de Churn

### Escenario 4.1: Mensaje con intención explícita de cancelar
- **DADO** un cliente Enterprise que envía el mensaje: *"Si esto continúa voy a cancelar mi suscripción anual."*
- **CUANDO** el `RiskEngine` evalúa las señales cualitativas.
- **ENTONCES** se suman los pesos determinísticos (Sentimiento Negativo +20, Frustración +20, Churn Intent +30, Soporte +10) aplicando el factor Enterprise (1.1x), resultando en un *Risk Score* $\ge 80$ y clasificación `CRITICAL`.

### Escenario 4.2: Mensaje positivo de felicitación
- **DADO** un cliente que envía: *"Excelente servicio, estoy muy satisfecho."*
- **CUANDO** el `RiskEngine` evalúa el feedback.
- **ENTONCES** se aplica una reducción de riesgo (Sentimiento Positivo -10, Satisfacción -5), el *Risk Score* final resulta $\le 29$ y se clasifica como `LOW`.

---

## 5. Motor de Alertas Críticas y Ciclo de Vida

### Escenario 5.1: Creación automática de alerta crítica
- **DADO** que una interacción produce un cálculo de riesgo con nivel `CRITICAL` ($Score \ge 80$).
- **CUANDO** finaliza la etapa de persistencia del cálculo.
- **ENTONCES** el `AlertService` inserta automáticamente un registro en la tabla `alerts` con estado `NEW`, severidad `CRITICAL` y el listado de motivos.

### Escenario 5.2: Transición de estado a ACKNOWLEDGED y RESOLVED
- **DADO** una alerta en estado `NEW` con id 5.
- **CUANDO** un operador envía `PATCH /api/v1/alerts/5` con `status = "ACKNOWLEDGED"`.
- **ENTONCES** la alerta actualiza su estado a `ACKNOWLEDGED` y registra el nombre del analista. Posteriormente, al enviar `status = "RESOLVED"` con notas de solución, pasa a `RESOLVED` y se cierra.

---

## 6. Dashboard y Visualización

### Escenario 6.1: Consumo unificado de datos del Dashboard
- **DADO** que el Dashboard frontend se carga en el navegador (`GET /`).
- **CUANDO** la aplicación invoca `GET /api/v1/dashboard`.
- **ENTONCES** la API responde en un solo payload los KPIs agregados, la serie temporal de evolución de 14 días, la distribución de sentimiento, las principales fricciones, las alertas críticas y la tabla de clientes.

---

## 7. Tolerancia a Fallos y Reintentos

### Escenario 7.1: Indisponibilidad temporal del proveedor LLM
- **DADO** que la API externa de IA se encuentra caída o responde con timeout.
- **CUANDO** entra una nueva interacción al pipeline.
- **ENTONCES** la interacción no se descarta; se almacena en la tabla `interactions` con estado `PENDING_AI_ANALYSIS`, se incrementa su `retry_count` y queda lista para ser reintentada automáticamente en el siguiente ciclo del scheduler.
