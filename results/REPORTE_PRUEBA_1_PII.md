# 📊 Reporte Oficial: PRUEBA 1 - Estrés de PII y Tokens Técnicos (50 Casos)
**Proyecto 6 — Monitor de Sentimiento de Clientes y Alertas de Riesgo de Abandono (Churn)**

**Fecha de Ejecución:** 2026-08-20 13:35:35 UTC  
**Entorno de Evaluación:** Local Python Engine (Zero External Dependencies)  
**Total de Casos Evaluados:** 50 casos  

---

## 📈 Resumen Ejecutivo de Métricas (Prueba 1)

| Métrica Evaluada | Resultado Obtenido | Meta / SLA | Estado |
|---|:---:|:---:|:---:|
| **Tasa de Detección de Churn** | **50 / 50 (100.0%)** | > 95% | ✅ APROBADO |
| **Alertas Críticas Emitidas** | **50 / 50 (100.0%)** | > 95% | ✅ APROBADO |
| **Entidades PII Sanitizadas** | **85 entidades** | 100% Cobertura | ✅ APROBADO |
| **Latencia Promedio por Caso** | **0.75 ms** | < 10 ms | ✅ APROBADO |
| **Tiempo Total (50 casos)** | **37.35 ms** | < 500 ms | ✅ APROBADO |
| **Tasa de Disponibilidad** | **100.0% (0 errores)** | 100% | ✅ APROBADO |

---

## 📋 Resultados Caso por Caso (Tabla Completa)

| ID | Categoría | Texto Saneado (Sin PII) | Sentimiento | Emoción | Fricción | Churn? | Risk Score | Nivel | Latencia |
|:---:|---|---|:---:|:---:|---|:---:|:---:|:---:|:---:|
| 1 | `PII_Inicio` | +57315[PHONE_MASKED]-[ID_DOC_MASKED]EUR quiero tra... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 6.49 ms |
| 2 | `PII_Inicio` | [ID_DOC_MASKED] solicito de manera irrevocable la ... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.52 ms |
| 3 | `PII_Inicio` | [BANK_ACCOUNT_MASKED]-CCV[CVC_MASKED] deseo rescin... | `negative` | `anger` | `billing_pricing` | 🚨 SÍ | **75/100** | `ALTO` | 0.5 ms |
| 4 | `PII_Inicio` | [IP_MASKED]-[IP_MASKED]-[IP_MASKED]-[ID_DOC_MASKED... | `negative` | `anger` | `customer_support` | 🚨 SÍ | **85/100** | `CRÍTICO` | 0.6 ms |
| 5 | `PII_Inicio` | [ID_DOC_MASKED]:PEJU800101-[ID_DOC_MASKED] procedo... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.48 ms |
| 6 | `PII_Inicio` | [ID_DOC_MASKED]:[SECRET_MASKED]:39281 ya no quiero... | `negative` | `anger` | `billing_pricing` | 🚨 SÍ | **75/100** | `ALTO` | 0.47 ms |
| 7 | `PII_Inicio` | [ID_DOC_MASKED]:12.345.678-X-BRL-SAOPAULO solicito... | `negative` | `anger` | `product_reliability` | 🚨 SÍ | **75/100** | `ALTO` | 0.53 ms |
| 8 | `PII_Inicio` | [GEO_MASKED]:-74.0721-[GEO_MASKED]:COL-BOGOTA-[GEO... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.55 ms |
| 9 | `PII_Inicio` | [TOKEN_MASKED] denme de baja inmediatamente de la ... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.3 ms |
| 10 | `PII_Inicio` | [ID_DOC_MASKED]:MEX-EXP:2030-AUT:SEGOB-[ID_DOC_MAS... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.54 ms |
| 11 | `PII_Final` | Solicito la baja inmediata. Registren mi [ID_DOC_M... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.46 ms |
| 12 | `PII_Final` | Quiero cancelar el plan contratado hoy mismo para ... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.43 ms |
| 13 | `PII_Final` | Deseo rescindir mi contrato de inmediato debido a ... | `negative` | `anger` | `billing_pricing` | 🚨 SÍ | **75/100** | `ALTO` | 0.46 ms |
| 14 | `PII_Final` | Ya no quiero seguir utilizando esta aplicacion ine... | `negative` | `anger` | `product_reliability` | 🚨 SÍ | **75/100** | `ALTO` | 0.91 ms |
| 15 | `PII_Final` | Procedo con la baja definitiva de todos los servic... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.48 ms |
| 16 | `PII_Final` | No voy a renovar la suscripcion el proximo mes baj... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.5 ms |
| 17 | `PII_Final` | Solicito el cierre de cuenta y remocion de datos f... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.58 ms |
| 18 | `PII_Final` | Exijo anular el contrato del modem satelital ubica... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.56 ms |
| 19 | `PII_Final` | Denme de baja del sistema corporativo inmediatamen... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.43 ms |
| 20 | `PII_Final` | Quiero rescindir de su plan de telefonia movil de ... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.55 ms |
| 21 | `PII_Sandwich` | Cerrar cuenta +57315[PHONE_MASKED]-[ID_DOC_MASKED]... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.35 ms |
| 22 | `PII_Sandwich` | Quiero la baja de [ID_DOC_MASKED] porque no uso el... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.35 ms |
| 23 | `PII_Sandwich` | Solicito rescindir [BANK_ACCOUNT_MASKED]-CCV[CVC_M... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.42 ms |
| 24 | `PII_Sandwich` | Exijo cancelar [IP_MASKED]-[IP_MASKED]-[IP_MASKED]... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.43 ms |
| 25 | `PII_Sandwich` | Tramitar baja de [ID_DOC_MASKED]:PEJU800101-[ID_DO... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.37 ms |
| 26 | `PII_Sandwich` | No renovar [ID_DOC_MASKED]:[SECRET_MASKED]:39281 d... | `negative` | `anger` | `billing_pricing` | 🚨 SÍ | **75/100** | `ALTO` | 0.42 ms |
| 27 | `PII_Sandwich` | Cerrar perfil [ID_DOC_MASKED]:12.345.678-X-BRL-SAO... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.46 ms |
| 28 | `PII_Sandwich` | Anular contrato [GEO_MASKED]:-74.0721-[GEO_MASKED]... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.47 ms |
| 29 | `PII_Sandwich` | Solicito cancelacion [TOKEN_MASKED] de inmediato s... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.28 ms |
| 30 | `PII_Sandwich` | Dar de baja [ID_DOC_MASKED]:MEX-EXP:2030-AUT:SEGOB... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.48 ms |
| 31 | `Logs_Sistema` | [LOG_MASKED] El cliente exige la cancelacion de cu... | `negative` | `anger` | `product_reliability` | 🚨 SÍ | **75/100** | `ALTO` | 0.37 ms |
| 32 | `Logs_Sistema` | [LOG_MASKED] el usuario se canso de esperar y pide... | `negative` | `anger` | `sla_delay` | 🚨 SÍ | **85/100** | `CRÍTICO` | 0.33 ms |
| 33 | `Logs_Sistema` | [LOG_MASKED] tramitar rescision de cuenta cloud. | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.24 ms |
| 34 | `Logs_Sistema` | [LOG_MASKED] deseo anular mi suscripcion por compl... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.28 ms |
| 35 | `Logs_Sistema` | [LOG_MASKED] dar de baja el servicio. | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.23 ms |
| 36 | `Logs_Sistema` | Quiero rescindir mi contrato de inmediato [LOG_MAS... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.27 ms |
| 37 | `Logs_Sistema` | Proceder con el cierre definitivo de la cuenta com... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.33 ms |
| 38 | `Logs_Sistema` | No deseo continuar con la renovacion automatica [L... | `negative` | `anger` | `billing_pricing` | 🚨 SÍ | **75/100** | `ALTO` | 0.29 ms |
| 39 | `Logs_Sistema` | Exijo la anulacion del cobro y la baja de la app [... | `negative` | `anger` | `billing_pricing` | 🚨 SÍ | **75/100** | `ALTO` | 0.34 ms |
| 40 | `Logs_Sistema` | [LOG_MASKED] El usuario solicita formalmente cance... | `negative` | `anger` | `customer_support` | 🚨 SÍ | **85/100** | `CRÍTICO` | 0.35 ms |
| 41 | `Web_URL_Params` | [URL_MASKED] deseo mi baja. | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.17 ms |
| 42 | `Web_URL_Params` | Quiero cancelar mi suscripcion desde este enlace [... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.28 ms |
| 43 | `Web_URL_Params` | Solicito la rescision del servicio web tracking_pi... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.5 ms |
| 44 | `Web_URL_Params` | No mas prorrogas, exijo dar de baja mi cuenta banc... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.4 ms |
| 45 | `Web_URL_Params` | [URL_MASKED] proceder con la cancelacion total. | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.24 ms |
| 46 | `Web_URL_Params` | Anular contrato de inmediato. Ref de navegacion: /... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.52 ms |
| 47 | `Web_URL_Params` | Deseo cerrar mi perfil corporativo de forma defini... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.5 ms |
| 48 | `Web_URL_Params` | [URL_MASKED] ya no los quiero. | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.19 ms |
| 49 | `Web_URL_Params` | Exijo la anulacion total de mi membresia activa co... | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.46 ms |
| 50 | `Web_URL_Params` | Tramitar baja inmediata. Vinculo: [URL_MASKED] | `negative` | `anger` | `none` | 🚨 SÍ | **75/100** | `ALTO` | 0.24 ms |
