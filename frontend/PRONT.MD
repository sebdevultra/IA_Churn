Aquí tienes la estructura completada y detallada, lista para usarla como prompt con cualquier asistente o generador de código para construir el frontend completo:

---

### Actúa Como:

Un **Frontend Architect & Senior UI/UX Developer** experto en JavaScript vanilla (ES6+), HTML5 semántico, CSS3 moderno (arquitectura modular, CSS Variables, Flexbox/Grid) y visualización de datos con **Chart.js**.

---

### Quiero:

Que desarrolles la interfaz completa y funcional para el **Monitor de Sentimiento de Clientes y Alertas de Riesgo de Abandono (Churn Sentinel AI)**, organizada bajo una arquitectura de archivos estática y desacoplada, sin frameworks pesados (React/Vue/Angular), garantizando máxima velocidad y responsividad.

---

### Para:

Permitir a los gerentes de operaciones y equipos de Customer Success:

1. Monitorear en tiempo real la salud de sentimiento y casos críticos de abandono.
2. Gestionar incidentes de alto riesgo directamente desde una consola de intervención (`PENDING` $\rightarrow$ `IN_REVIEW` $\rightarrow$ `RESOLVED`).
3. Probar en vivo la clasificación del pipeline de IA mediante un simulador de ingesta interactivo.

---

## Requisitos:

**1. Estructura de Archivos a Generar**

* `index.html`: Estructura semántica, accesible (WAI-ARIA) y layout completo.
* `css/main.css`: Variables CSS (paleta de colores, tipografías, spacing, temas) y reset base.
* `css/components.css`: Estilos para KPI cards, tablas interactivas, badges de severidad, modales, alertas toast y grid responsivo.
* `js/api_client.js`: Capa de consumo HTTP con `fetch` async/await, tipado JSDoc y manejo de reintentos y errores de red.
* `js/charts.js`: Configuración e inicialización de gráficos interactivos con **Chart.js** (Línea para tendencia 30d y Barras horizontales para fricciones).
* `js/ui_controller.js`: Renderizado dinámico de KPIs, tabla de riesgo, estados de badges, modales de detalle y toasts no intrusivos.
* `js/app.js`: Orquestador global, control de eventos del DOM, sondeo inteligente (*polling* configurable) y lógica del simulador en vivo.

**2. Componentes y Layout de la UI**

* **Barra Superior / Header:** Nombre del sistema, semáforo de alertas críticas activas y switch toggle de auto-refresh / estado de conexión.
* **4 KPI Cards Ejecutivos:** Total de interacciones, Índice de Salud (% tri-color), NPS Predictivo y Casos en Riesgo (Naranja: Alto, Rojo: Crítico).
* **Zona de Gráficos:**
* *Evolución Temporal del Sentimiento:* Gráfico de líneas/área con 3 series (Positivo, Neutro, Negativo).
* *Puntos de Fricción:* Gráfico de barras horizontales ordenado de mayor a menor frecuencia (`customer_support`, `billing_pricing`, `product_reliability`, `sla_delay`, `feature_gap`).


* **Tabla de Casos Críticos & Consola de Intervención:**
* Columnas: Cliente, Tier, Risk Score (badge 0–100), Emoción/Fricción, Evidencia textual (con PII enmascarada) y Botón de acción rápida.
* Filtros de tabla: *Todos*, *Solo Críticos*, *Pendientes*, y buscador por texto.
* Modal de Detalle: Muestra desglose del score (factores $+30, +20$, etc.), motor de IA usado y formulario para cambiar estado (`PENDING` / `IN_REVIEW` / `RESOLVED`).


* **Testbed / Simulador de Ingesta en Vivo:**
* Formulario con textarea, botones rápidos de prueba predefinidos (*"Positivo"*, *"Frustración soporte"*, *"Amenaza de cancelación"*, *"Sarcasmo"*), y botón *Analizar en Vivo* que dispara `POST /api/interactions` y actualiza la UI al instante.



**3. Integración de API & Sincronización**

* Implementar polling periódico inteligente:
* Cada **5 segundos**: `/api/analytics/kpis` y `/api/churn/high-risk`.
* Cada **15 segundos**: `/api/analytics/sentiment-trend` y `/api/analytics/friction-distribution`.


* Endpoints bajo demanda:
* `PATCH /api/alerts/{id}`: Actualización de estado de la alerta.
* `POST /api/interactions`: Inyección de feedback desde el testbed.


* Resiliencia de red: Si el servidor falla o no responde, mostrar un toast de reconexión sin romper el estado actual de los gráficos ni congelar la pantalla.

**4. Criterios de Código y Calidad**

* Código limpio, modular, comentado y sin dependencias externas excepto CDN de Chart.js.
* Diseño 100% responsivo (Desktop 1920x1080, Laptop 1366x768 y Tablet 768px).
* Evita el uso el emojis en el codigo y en la pagina.
* Usa iconos en la pagina en lugar de emojis para que sea mas profesional.




### Actúa Como:
Un **Frontend Architect & Senior UI/UX Developer** experto en JavaScript vanilla modular (ES6+), HTML5 semántico accesible (WAI-ARIA), CSS3 moderno (Variables CSS, Flexbox, CSS Grid) y visualización de datos con **Chart.js**.

---

### Objetivo:
Desarrollar la interfaz completa, funcional y altamente profesional para el **Monitor de Sentimiento de Clientes y Alertas de Riesgo de Abandono (Churn Sentinel AI)**, organizada bajo una arquitectura de archivos estática y desacoplada, sin frameworks pesados (React/Vue/Angular), garantizando máxima velocidad, reactividad y diseño corporativo.

---

### Requisitos Técnicos y de Negocio:

#### 1. Estructura de Archivos a Generar
* `index.html`: Estructura semántica, accesible y layout responsivo. Integrar Font Awesome o Lucide Icons vía CDN y Chart.js.
* `css/main.css`: Variables de diseño (paleta Slate/Indigo profesional, tipografía Inter/system-ui, espaciados y reset base).
* `css/components.css`: Estilos para KPI cards, tablas interactivas, badges de severidad por rangos, modales, alertas toast y grid responsivo.
* `js/api_client.js`: Módulo de consumo HTTP con `fetch` async/await, tipado JSDoc, manejo de errores y reintentos.
* `js/charts.js`: Configuración e inicialización de gráficos Chart.js (Líneas/Área para tendencia 30d y Barras horizontales para fricciones).
* `js/ui_controller.js`: Renderizado dinámico de KPIs, tabla de riesgo, estados de badges, modales de detalle y toasts no intrusivos.
* `js/app.js`: Orquestador global, control de eventos del DOM, sondeo periódico inteligente (polling) y lógica del simulador en vivo.

#### 2. Componentes y Layout de la UI
* **Barra Superior / Header:** Nombre del sistema, badge con contador de alertas críticas activas, botón toggle de auto-refresh y estado de conexión (Online/Offline).
* **4 KPI Cards Ejecutivos:** Total de interacciones procesadas, Índice de Salud (% Positivo/Neutro/Negativo con barra tri-color), NPS Predictivo y Casos en Riesgo (Desglose Alto vs Crítico).
* **Zona de Gráficos:**
  * *Evolución Temporal del Sentimiento (30d):* Gráfico de líneas con 3 series (Positivo: Verde, Neutro: Azul/Gris, Negativo: Rojo).
  * *Puntos de Fricción:* Gráfico de barras horizontales ordenado de mayor a menor frecuencia (`customer_support`, `billing_pricing`, `product_reliability`, `sla_delay`, `feature_gap`).
* **Tabla de Casos Críticos & Consola de Intervención:**
  * Columnas: Cliente, Tier (Enterprise, Pro, Standard), Risk Score (Badge: 0-29 Verde, 30-59 Amarillo, 60-79 Naranja, 80-100 Rojo), Emoción/Fricción, Evidencia textual (con PII enmascarada) y Botón de acción rápida ("Gestionar").
  * Filtros de tabla: *Todos*, *Solo Críticos*, *Pendientes* y campo de búsqueda por texto.
  * Modal de Detalle: Muestra desglose de factores de score (+20 sentimiento, +30 intención de cancelación, etc.), motor de IA utilizado (`cloud_gemini` vs `local_nlp`) y formulario para cambiar estado (`PENDING` -> `IN_REVIEW` -> `RESOLVED`) con campo de notas.
* **Testbed / Simulador de Ingesta en Vivo:**
  * Formulario con selector de cliente/tier, textarea para el feedback y botones de prueba rápida (*"Positivo"*, *"Frustración soporte"*, *"Amenaza de cancelación"*, *"Sarcasmo"*).
  * Botón *Analizar en Vivo* que realiza `POST /api/interactions` y actualiza inmediatamente la UI y los gráficos sin recargar la página.

#### 3. Integración de API & Sincronización
* **Polling Inteligente:**
  * Cada **5 segundos**: `GET /api/analytics/kpis` y `GET /api/churn/high-risk`.
  * Cada **15 segundos**: `GET /api/analytics/sentiment-trend` y `GET /api/analytics/friction-distribution`.
* **Endpoints Bajo Demanda:**
  * `PATCH /api/alerts/{id}`: Actualización de estado de la alerta.
  * `POST /api/interactions`: Inyección de nuevo feedback.
* **Resiliencia de Red:** Ante errores o desconexión del servidor, mostrar una notificación toast no intrusiva, reintentar automáticamente en el siguiente ciclo y preservar el estado visual de los gráficos.

#### 4. Criterios de Calidad y Estilo
* **Sin Emojis:** Prohibido el uso de emojis tanto en el código como en la interfaz visual.
* **Iconografía Profesional:** Utilizar iconos vectoriales (Font Awesome o SVG inline) para todas las acciones, badges y métricas.
* **Diseño 100% Responsivo:** Adaptable a Desktop (1920x1080), Laptop (1366x768) y Tablet (768px).
* **Código Limpio:** JavaScript modular, modularidad CSS, comentarios explicativos y sin librerías externas adicionales más allá de Chart.js y los iconos.