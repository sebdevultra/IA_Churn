# 🎨 Plan de Implementación: Frontend & Integration Lead
**Proyecto 6 — Monitor de Sentimiento de Clientes y Alertas de Riesgo de Abandono (Churn)**

*Guía técnica y de experiencia de usuario (UX) para el desarrollo del Dashboard analítico, visualizaciones interactivas, consola de incidentes y sincronización con la API y el Pipeline de Automatización.*

---

## 🎯 1. Objetivo y Responsabilidades del Rol

Como **Frontend & Integration Lead**, tu misión es transformar los datos procesados y las alertas en una experiencia visual accionable, intuitiva y en tiempo real para gerentes de operaciones y equipos de Customer Success.
Tus responsabilidades principales son:
1. **Dashboard Analítico Reactivo:** Construir la interfaz de usuario (HTML5, CSS3 moderno, JavaScript ES6+ modular, Chart.js) sin dependencias excesivas para máxima velocidad.
2. **Visualización de KPIs y Tendencias:** Renderizar gráficos de distribución de sentimiento, evolución temporal y mapa de fricciones operativas.
3. **Consola de Intervención y Gestión de Alertas:** Diseñar la bandeja de incidentes de alto riesgo (`Alto` / `Crítico`) con capacidad de cambiar estados a un clic (`PENDING` → `IN_REVIEW` → `RESOLVED`).
4. **Consola de Ingesta & Testbed en Vivo:** Permitir a los evaluadores inyectar reseñas o mensajes de prueba en vivo y ver la respuesta instantánea del pipeline de IA y el Risk Engine.
5. **Sincronización y Resiliencia UI:** Implementar sondeo periódico inteligente (*polling* cada 5s configurable), indicadores de carga, manejo elegante de errores y modales de detalle con evidencia textual.

---

## 🖥️ 2. Arquitectura Visual y Layout del Dashboard

```text
+-----------------------------------------------------------------------------------------------+
| 📊 CHURN SENTINEL AI - Monitor de Sentimiento & Alertas de Abandono     [🔴 3 Alertas Críticas] [🔄 Auto-refresh: ON] |
+-----------------------------------------------------------------------------------------------+
| [ KPIs SUPERIORES ]                                                                           |
| +-------------------+  +-------------------+  +--------------------+  +---------------------+ |
| | Total Clientes:   |  | Sentimiento Neto: |  | NPS Estimado:      |  | Casos en Riesgo:    | |
| | 1,240             |  | +42% Positivo     |  | +38 (Saludable)    |  | 14 (8 Críticos)      | |
| +-------------------+  +-------------------+  +--------------------+  +---------------------+ |
+-----------------------------------------------------------------------------------------------+
| [ GRÁFICOS ANALÍTICOS ]                                                                       |
| +-----------------------------------------------+  +----------------------------------------+ |
| | 📈 Evolución Temporal del Sentimiento (30d)    |  | 🌪️ Puntos de Fricción Principales       | |
| | [ Gráfico de Líneas con Chart.js ]            |  | [ Gráfico de Barras Horizontales ]     | |
| | (Positivo vs Neutro vs Negativo)              |  | (Soporte, Facturación, Bugs, SLA, UX)  | |
| +-----------------------------------------------+  +----------------------------------------+ |
+-----------------------------------------------------------------------------------------------+
| [ TABLERO DE CASOS DE ALTO RIESGO & ALERTAS ACCIONABLES ]                                      |
| [Filtros: Todos | Solo Críticos | Pendientes] [Buscar cliente...]                             |
| +------------+-----------+------------+---------------+--------------------+----------------+ |
| | Cliente    | Tier      | Risk Score | Fricción      | Evidencia Semántica| Acciones       | |
| +------------+-----------+------------+---------------+--------------------+----------------+ |
| | TechCorp   |Enterprise | 🚨 90 pts  | Facturación   | "Cancelo contrato" | [Gestionar]    | |
| | GlobalLog  | Pro       | ⚠️ 75 pts  | Soporte / SLA | "3 días sin rta"   | [Ver Detalle]  | |
| +------------+-----------+------------+---------------+--------------------+----------------+ |
+-----------------------------------------------------------------------------------------------+
| [ SIMULADOR DE INGESTA EN VIVO / TESTBED ]                                                     |
| Ingrese un mensaje de cliente para probar el análisis en tiempo real:                          |
| [ "Excelente servicio, pero el aumento de precio nos obliga a buscar alternativas..."      ]  |
| [ Botón: Analizar en Vivo ] -> [ Chip: IA Local/Cloud ] [ Score: 65 - Alto ] [ Fricción: Pricing ]|
+-----------------------------------------------------------------------------------------------+
```

---

## 🎨 3. Especificación de Componentes UI

### 3.1 Tarjetas de KPIs Ejecutivos
- **Total de Interacciones Procesadas:** Contador incremental.
- **Índice de Salud de Sentimiento:** % Positivo / Neutro / Negativo con barra de progreso tri-color.
- **NPS Predictivo:** Cálculo $(\% \text{Promotores} - \% \text{Detractores})$.
- **Semáforo de Churn:** Contador de clientes en nivel `Alto` (naranja) y `Crítico` (rojo).

### 3.2 Visualizaciones con Chart.js
1. **Gráfico de Línea / Área (`sentimentTrendChart`):**
   - Eje X: Fechas (últimos 30 días o agrupado por semanas).
   - Eje Y: Cantidad de interacciones clasificadas por la IA.
   - Series: Verde (Positivo), Gris/Azul (Neutro), Rojo (Negativo).
2. **Gráfico de Barras (`frictionChart`):**
   - Categorías: `customer_support`, `billing_pricing`, `product_reliability`, `sla_delay`, `feature_gap`.
   - Ordenado descendentemente por frecuencia de quejas.

### 3.3 Tabla Dinámica de Casos Críticos
- Cada fila incluye:
  - Nombre del cliente y etiqueta de Tier (`Enterprise`, `Pro`, `Standard`).
  - Medidor de Riesgo de Churn (Badge con color según el rango: 0-29 Verde, 30-59 Amarillo, 60-79 Naranja, 80-100 Rojo).
  - Emoción detectada (`frustration`, `anger`, `confusion`).
  - Extracto de evidencia textual detectada por la IA (con tooltip o modal para ver el mensaje completo anonimizado).
  - Botón de Acción Rápida: Abrir modal de intervención para marcar como resuelta, asignar a un CSM o añadir notas.

### 3.4 Modal de Detalle de Intervención
- Muestra el historial del cliente, desglose de factores de score de churn (ej: $+20$ sentimiento, $+30$ intención de cancelar, $+10$ soporte), motor de IA utilizado (`cloud_gemini` vs `local_nlp`), y formulario para registrar la resolución.

### 3.5 Testbed / Simulador de Ingesta en Vivo
- Un formulario interactivo con botones rápidos de prueba predefinidos:
  - *"Mensaje Positivo"*
  - *"Frustración por soporte"*
  - *"Amenaza de cancelación Enterprise"*
  - *"Sarcasmo / Ironía"*
- Al enviar, hace un `POST /api/interactions` y actualiza inmediatamente la UI sin necesidad de refrescar la página.

---

## 📁 4. Estructura de Archivos Recomendada para Frontend

```text
static/
├── index.html                # Estructura semántica, accesibilidad y layout responsivo
├── css/
│   ├── main.css              # Variables de diseño (colores corporativos, tipografía, badges)
│   └── components.css        # Estilos de tablas, modales, alertas, cards y responsive grid
├── js/
│   ├── api_client.js         # Wrapper modular con fetch async/await para endpoints del Backend
│   ├── charts.js             # Configuración e instanciación de gráficos Chart.js
│   ├── ui_controller.js      # Renderizado de tablas, modales, toasts y formateadores de badges
│   └── app.js                # Orquestador: polling periódico, eventos DOM y simulador en vivo
└── assets/
    └── favicon.ico
```

---

## 🔌 5. Integración con los Endpoints del Backend

| Endpoint Backend | Método | Función en Frontend | Frecuencia |
|---|---|---|---|
| `/api/analytics/kpis` | `GET` | Actualiza los 4 contadores superiores | Polling cada 5 seg |
| `/api/analytics/sentiment-trend` | `GET` | Actualiza el gráfico de evolución temporal | Polling cada 15 seg |
| `/api/analytics/friction-distribution` | `GET` | Actualiza el gráfico de barras de fricción | Polling cada 15 seg |
| `/api/churn/high-risk` | `GET` | Renderiza la tabla de clientes en riesgo | Polling cada 5 seg |
| `/api/alerts/{id}` | `PATCH` | Actualiza el estado de la alerta tras intervención | On-demand (clic usuario) |
| `/api/interactions` | `POST` | Envía feedback desde el simulador en vivo | On-demand (formulario) |

---

## 🧪 6. Plan de Validación de Interfaz y Flujos

1. **Prueba de Flujo Completo (Happy Path):** Enviar un mensaje de frustración en el simulador $\rightarrow$ verificar que el KPI de riesgo aumenta $\rightarrow$ verificar que aparece la alerta en la tabla $\rightarrow$ resolver la alerta y verificar el cambio de badge a `RESOLVED`.
2. **Prueba de Resiliencia de Red:** Simular corte de conexión con el backend $\rightarrow$ la UI debe mostrar un toast de aviso no intrusivo y reintentar la conexión en el siguiente ciclo sin romper los gráficos.
3. **Prueba de Responsividad:** Validar correcta visualización en resolución Desktop (1920x1080), Laptop (1366x768) y Tablet (768px).
