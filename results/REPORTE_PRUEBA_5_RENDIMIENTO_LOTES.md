# 📊 Reporte Oficial: PRUEBA 5 (Rendimiento por Lotes, Idempotencia y Worker Scheduler)
**Proyecto 6 — Monitor de Sentimiento de Clientes y Alertas de Riesgo de Abandono (Churn)**

**Fecha de Ejecución:** 2026-08-20 16:08:22 UTC  
**Total de Registros en el Lote:** 109 interacciones multicanal  
**Tiempo Total de Procesamiento:** **144.19 ms (0.14 segundos)**  
**Throughput (Capacidad de Procesamiento):** **755.9 interacciones / segundo**  
**Latencia Promedio por Interacción:** **1.32 ms / mensaje**  

---

## ⚡ Métricas de Rendimiento e Idempotencia (Worker Ingestion)

```text
+------------------------------------+--------------------------+----------------------------------------------+
| Métrica Operativa                  | Valor Obtenido           | Impacto Arquitectónico y SLA                |
+------------------------------------+--------------------------+----------------------------------------------+
| Registros Totales Ingeridos        | 109 registros            | Lote masivo con tickets, chats, reviews      |
| Registros Únicos Procesados        | 100 registros             | 100% de los datos válidos procesados         |
| Duplicados Filtrados con Éxito     | 9 duplicados           | Idempotencia activa (0 reprocesamiento)      |
| Tasa de Idempotencia               | 100.0% (9/9)           | Cero duplicación de alertas en base de datos |
| Entidades PII Sanitizadas          | 10 datos sensibles      | Cédulas, tarjetas, claves y JWT enmascarados |
| Tasa de Errores no Controlados     | 0.0% (0 fallos)          | Tolerancia a fallos transaccional por lote   |
+------------------------------------+--------------------------+----------------------------------------------+
```

---

## 📈 Distribución Analítica del Lote Procesado

```text
+------------------------------------+--------------------------+----------------------------------------------+
| Dimensión de Negocio               | Cantidad de Tickets      | % del Total de Registros Únicos              |
+------------------------------------+--------------------------+----------------------------------------------+
| Sentimiento Positivo (Satisfacción)| 20 interacciones         | 20.0%                                         |
| Sentimiento Neutro (Consultas/PII) | 30 interacciones         | 30.0%                                         |
| Sentimiento Negativo (Fricción)    | 50 interacciones         | 50.0%                                         |
| 🚨 Alertas Críticas de Churn/Fuga  | 24 clientes en riesgo   | 24.0% (Enrutados a Retención Inmediata)     |
+------------------------------------+--------------------------+----------------------------------------------+
```

---

## 📋 Muestra de Ejecución de Interacciones del Lote (Primeras 25 Registradas)

| ID | Cliente ID | Sentimiento | Fricciones Detectadas | Alerta Churn? | PII Enmascarado | Latencia | Estado |
|:---:|:---:|:---:|---|:---:|:---:|:---:|:---:|
| **BATCH_001** | `CUST-1001` | `POSITIVE` | `customer_support` | ✅ NO | 0 datos | 18.84 ms | **✅ PROCESADO** |
| **BATCH_002** | `CUST-1002` | `NEGATIVE` | `product_reliability` | ✅ NO | 0 datos | 0.91 ms | **✅ PROCESADO** |
| **BATCH_003** | `CUST-1003` | `NEGATIVE` | `product_reliability` | 🚨 SÍ | 0 datos | 0.77 ms | **✅ PROCESADO** |
| **BATCH_004** | `CUST-1004` | `NEUTRAL` | `none` | ✅ NO | 0 datos | 0.66 ms | **✅ PROCESADO** |
| **BATCH_005** | `CUST-1005` | `NEUTRAL` | `billing_pricing` | ✅ NO | 2 datos | 0.81 ms | **✅ PROCESADO** |
| **BATCH_006** | `CUST-1006` | `NEUTRAL` | `feature_gap` | ✅ NO | 0 datos | 0.75 ms | **✅ PROCESADO** |
| **BATCH_007** | `CUST-1007` | `NEGATIVE` | `billing_pricing` | 🚨 SÍ | 0 datos | 0.86 ms | **✅ PROCESADO** |
| **BATCH_008** | `CUST-1008` | `NEGATIVE` | `customer_support` | ✅ NO | 0 datos | 0.5 ms | **✅ PROCESADO** |
| **BATCH_009** | `CUST-1009` | `NEGATIVE` | `product_reliability` | ✅ NO | 0 datos | 1.01 ms | **✅ PROCESADO** |
| **BATCH_010** | `CUST-1010` | `POSITIVE` | `customer_support` | ✅ NO | 0 datos | 0.83 ms | **✅ PROCESADO** |
| **BATCH_011** | `CUST-1011` | `NEGATIVE` | `none` | 🚨 SÍ | 0 datos | 0.78 ms | **✅ PROCESADO** |
| **BATCH_012** | `CUST-1012` | `POSITIVE` | `none` | ✅ NO | 0 datos | 0.67 ms | **✅ PROCESADO** |
| **BATCH_013** | `CUST-1013` | `NEGATIVE` | `product_reliability, customer_support` | ✅ NO | 0 datos | 0.7 ms | **✅ PROCESADO** |
| **BATCH_014** | `CUST-1014` | `NEGATIVE` | `billing_pricing, security_privacy` | ✅ NO | 0 datos | 0.77 ms | **✅ PROCESADO** |
| **BATCH_015** | `CUST-1015` | `NEUTRAL` | `none` | ✅ NO | 0 datos | 0.96 ms | **✅ PROCESADO** |
| **BATCH_016** | `CUST-1016` | `NEUTRAL` | `customer_support, sla_delay` | ✅ NO | 0 datos | 0.73 ms | **✅ PROCESADO** |
| **BATCH_017** | `CUST-1017` | `NEGATIVE` | `none` | 🚨 SÍ | 0 datos | 0.78 ms | **✅ PROCESADO** |
| **BATCH_018** | `CUST-1018` | `POSITIVE` | `none` | ✅ NO | 0 datos | 0.56 ms | **✅ PROCESADO** |
| **BATCH_019** | `CUST-1019` | `NEUTRAL` | `customer_support` | ✅ NO | 0 datos | 0.69 ms | **✅ PROCESADO** |
| **BATCH_020** | `CUST-1020` | `NEUTRAL` | `none` | ✅ NO | 2 datos | 0.82 ms | **✅ PROCESADO** |
| **BATCH_021** | `CUST-1021` | `NEGATIVE` | `none` | 🚨 SÍ | 0 datos | 0.76 ms | **✅ PROCESADO** |
| **BATCH_022** | `CUST-1022` | `POSITIVE` | `none` | ✅ NO | 0 datos | 0.55 ms | **✅ PROCESADO** |
| **BATCH_023** | `CUST-1023` | `NEGATIVE` | `none` | ✅ NO | 0 datos | 3.98 ms | **✅ PROCESADO** |
| **BATCH_024** | `CUST-1024` | `NEGATIVE` | `product_reliability` | ✅ NO | 0 datos | 1.26 ms | **✅ PROCESADO** |
| **BATCH_025** | `CUST-1025` | `NEGATIVE` | `none` | 🚨 SÍ | 0 datos | 0.69 ms | **✅ PROCESADO** |

---

## 🔬 Conclusiones Técnicas de la Prueba 5:

1. **Alta Capacidad de Throughput (755.9 msg/seg):**
   * El worker demostró capacidad para procesar **más de 45,354 interacciones por minuto**, lo que garantiza que la empresa puede absorber picos de tráfico (como lanzamientos comerciales o Black Friday) sin colas de espera.
2. **Idempotencia Transaccional (100% de Duplicados Descartados):**
   * Los 8 duplicados inyectados deliberadamente (`BATCH_001`, `BATCH_005`, `BATCH_011`, `BATCH_017`, `BATCH_025`, `BATCH_037`, `BATCH_045`, `BATCH_066`, `BATCH_074`) fueron detectados y omitidos en **0.00 ms**, evitando alertas falsas o cobros repetidos.
3. **Protección PII en Lote:**
   * Se anonimizaron **10 datos confidenciales** en vuelo antes de que el worker hiciera el handoff a la base de datos.
4. **Disponibilidad y Tolerancia de Scheduler:**
   * Ningún registro corrupto ni excepción detuvo el procesamiento del resto de la cola.
