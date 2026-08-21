"""
Generador de Datasets Sintéticos de Estrés para Churn Sentinel AI.
Genera dos archivos CSV limpios y optimizados:
1. data/dataset_10k_interactions.csv   (10,000 registros)
2. data/dataset_1m_interactions.csv    (1,000,000 registros)
"""
import os
import csv
import time
import random

project_root = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(project_root, "data")
os.makedirs(data_dir, exist_ok=True)

# Plantillas representativas por categoría
TEMPLATES = [
    # 1. Críticas / Amenazas de Churn
    ("support_ticket", "Enterprise", "El tiempo de inactividad de la base de datos superó el SLA pactado. Si no resuelven hoy cancelamos el contrato corporativo."),
    ("review", "Enterprise", "Exijo la devolución total de la mensualidad; el servicio es inestable y migraremos a otro proveedor este fin de semana."),
    ("support_ticket", "Enterprise", "Cobro duplicado en nuestra tarjeta de crédito empresarial y soporte no contesta nuestros correos de alta prioridad."),
    ("nps_survey", "Enterprise", "Solicito la baja definitiva de nuestros 50 accesos de equipo por caídas continuas."),
    ("chat", "Enterprise", "La junta directiva autorizó rescindir el contrato inmediatamente debido a los fallos en producción."),
    
    # 2. Sarcasmo / Ironía
    ("review", "Enterprise", "Fantástico servicio, me encanta pagar el doble por un software que se congela todo el día y no deja exportar datos."),
    ("support_ticket", "Enterprise", "Genios absolutos, cobraron el triple en la factura de este mes y borraron los accesos de auditoría."),
    ("chat", "Pro", "Una maravilla su plataforma... borró la base de datos y nadie responde en el chat."),
    ("review", "Standard", "Hermoso soporte, 3 días esperando respuesta para que me digan que reinicie la máquina."),
    
    # 3. Fricciones y Problemas Operativos
    ("support_ticket", "Pro", "La API devuelve error 500 intermitente cada vez que enviamos más de 100 consultas por minuto."),
    ("chat", "Standard", "No me llega el correo de verificación para restablecer la contraseña."),
    ("support_ticket", "Standard", "El botón de descargar reportes en formato PDF y Excel no responde en el navegador."),
    ("support_ticket", "Pro", "Llevamos más de 48 horas esperando respuesta al ticket de soporte urgente."),
    ("chat", "Enterprise", "La latencia de sincronización empeoró drásticamente después del último despliegue."),
    ("support_ticket", "Standard", "Inconsistencia en los totales facturados durante el cierre del mes anterior."),
    
    # 4. Positivas y Alta Satisfacción
    ("nps_survey", "Enterprise", "Excelente herramienta, optimizó el tiempo de nuestro equipo comercial de forma notable."),
    ("review", "Standard", "Muy fácil de usar, la interfaz es moderna y muy intuitiva."),
    ("chat", "Pro", "Muchas gracias por solucionar nuestro inconveniente en menos de 10 minutos, gran atención."),
    ("nps_survey", "Pro", "Plataforma 100% recomendada para gestión corporativa, gran rendimiento y soporte."),
    ("review", "Enterprise", "Todo perfecto con el proceso de onboarding y la integración de webhooks."),
    
    # 5. Neutras y Consultas Generales
    ("chat", "Standard", "¿Dónde puedo consultar la documentación técnica sobre la integración con Webhooks?"),
    ("support_ticket", "Pro", "Solicitud de información sobre los nuevos planes comerciales y límites de consumo de API."),
    ("chat", "Standard", "Buenas tardes, quería consultar sobre las opciones de pago mediante transferencia bancaria."),
    ("nps_survey", "Standard", "El sistema cumple con lo esperado para nuestras necesidades actuales."),
    ("chat", "Pro", "¿Tienen previsto agregar soporte para exportación directa a BigQuery en el próximo release?")
]

TIERS = ["Enterprise", "Pro", "Standard"]
CHANNELS = ["support_ticket", "chat", "review", "nps_survey"]


def generate_dataset(file_name: str, total_rows: int):
    target_path = os.path.join(data_dir, file_name)
    print(f"[*] Iniciando generación de {file_name} ({total_rows:,} registros)...")
    start_time = time.time()

    # Buffer de escritura optimizado para máximo throughput I/O
    chunk_size = 50000
    rows_buffer = []

    with open(target_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Encabezados limpios estándar
        writer.writerow(["customer_external_id", "source_type", "tier", "content", "external_reference_id"])

        num_templates = len(TEMPLATES)
        for i in range(1, total_rows + 1):
            tmpl_channel, tmpl_tier, tmpl_content = TEMPLATES[i % num_templates]
            
            cust_num = (i % 1200) + 1001
            cust_id = f"CUST-{cust_num}"
            ref_id = f"EVT-{i:07d}"

            # Añadir variación de contenido para evitar hashes duplicados
            variation_suffix = f" (Ref: #{i})"
            content = tmpl_content + (variation_suffix if i > num_templates else "")

            rows_buffer.append([cust_id, tmpl_channel, tmpl_tier, content, ref_id])

            if len(rows_buffer) >= chunk_size:
                writer.writerows(rows_buffer)
                rows_buffer.clear()
                elapsed = time.time() - start_time
                print(f"  -> Progreso: {i:,} / {total_rows:,} filas escritas ({elapsed:.1f}s)...")

        if rows_buffer:
            writer.writerows(rows_buffer)
            rows_buffer.clear()

    file_size_mb = os.path.getsize(target_path) / (1024 * 1024)
    duration = time.time() - start_time
    print(f"[OK] Generado exitosamente {file_name}:")
    print(f"     - Filas totales: {total_rows:,}")
    print(f"     - Tamaño en disco: {file_size_mb:.2f} MB")
    print(f"     - Tiempo transcurrido: {duration:.2f} segundos")
    print(f"     - Ruta: {target_path}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("   GENERADOR DE DATASETS CSV PARA CHURN SENTINEL AI")
    print("=" * 70)
    
    # 1. Dataset de 10,000 registros
    generate_dataset("dataset_10k_interactions.csv", 10000)

    # 2. Dataset de 1,000,000 registros
    generate_dataset("dataset_1m_interactions.csv", 1000000)

    print("=" * 70)
    print("   GENERACIÓN COMPLETADA CON ÉXITO")
    print("=" * 70)
