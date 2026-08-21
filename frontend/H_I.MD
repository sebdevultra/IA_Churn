**Historia de Usuario: Detección Temprana y Gestión de Clientes en Riesgo de Churn**

**ID:** HU-001

**Título:** Visualización y gestión de alertas de riesgo de abandono en tiempo real

**Épica:** Monitor de Sentimiento y Retención de Clientes

**Estimación:** 5 Story Points

**Prioridad:** Alta

---

**Descripción**

> **Como** Líder de Customer Success / Gerente de Operaciones,
> **quiero** visualizar en un tablero centralizado los clientes clasificados con riesgo de abandono alto o crítico junto con la causa de fricción y su evidencia textual,
> **para** intervenir proactivamente antes de que cancelen el servicio y gestionar la resolución del caso en un flujo claro.

---

**Criterios de Aceptación (Gherkin)**

* **Escenario 1: Detección y despliegue de caso crítico**
* **Dado** que el motor de riesgo procesa una interacción y calcula un puntaje $\ge 80$ pts,
* **Cuando** consulto la consola de alertas o se ejecuta el sondeo periódico (5s),
* **Entonces** el cliente debe aparecer en la tabla de casos críticos con su badge rojo, el nivel de severidad, el punto de fricción detectado y un extracto de la evidencia textual.


* **Escenario 2: Cambio de estado de intervención transaccional**
* **Dado** que un caso se encuentra en estado `PENDING`,
* **Cuando** hago clic en el botón de acción rápida y selecciono `IN_REVIEW` o `RESOLVED`,
* **Entonces** el sistema debe enviar un `PATCH /api/alerts/{id}`, actualizar el badge de estado inmediatamente en la UI y evitar disparar alertas duplicadas para ese cliente durante el período de enfriamiento (*cooldown*).


* **Escenario 3: Acceso a desglose analítico en modal**
* **Dado** un cliente listado en la tabla de riesgo,
* **Cuando** abro el modal de detalle,
* **Entonces** debo visualizar el desglose del puntaje de riesgo (ej. $+30$ intención de cancelación, $+20$ sentimiento negativo), el motor de inferencia utilizado (`local_nlp` o `cloud_gemini`) y el historial de interacciones previas.



---

**Criterios Técnicos / Definición de Hecho (DoD)**

* El endpoint `GET /api/churn/high-risk` debe responder en $<200$ ms.
* Los datos personales en la evidencia textual deben presentarse sanitizados (sin correos, teléfonos ni nombres reales).
* Cobertura de pruebas unitarias $\ge 90\%$ en la capa de persistencia y lógica de actualización de alertas.
* La interfaz debe ser completamente responsiva y mostrar alertas de reconexión si el servidor no responde durante el *polling*.