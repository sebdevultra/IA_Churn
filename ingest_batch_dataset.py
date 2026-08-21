"""
Script de Ingesta Masiva de Datos para Churn Sentinel AI.
Lee el dataset de prueba (CSV) y procesa las interacciones a través del AI Pipeline completo.
"""
import os
import sys
import csv
import time

project_root = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.join(project_root, "backend")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.app.db.session import SessionLocal
from backend.app.schemas.interaction import InteractionCreate
from backend.app.services.ingestion_service import IngestionPipelineService
from backend.app.models.customer import Customer
from backend.app.models.interaction import Interaction


def run_batch_ingest():
    csv_path = os.path.join(project_root, "results", "dataset_prueba_5_batch_ingestion.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(project_root, "backend", "data", "sample_interactions.csv")

    print("=" * 70)
    print("   INICIANDO INGESTA MASIVA DE DATASET CSV")
    print(f"   Archivo Fuente: {csv_path}")
    print("=" * 70)

    db = SessionLocal()
    processed = 0
    duplicates = 0
    errors = 0
    start_time = time.time()

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalizar nombres de columnas del CSV
                cust_id = row.get("Cliente_ID") or row.get("customer_external_id") or row.get("customer_id") or "CUST-GENERIC"
                channel = row.get("Canal") or row.get("source_type") or "support_ticket"
                tier = row.get("Tier") or row.get("customer_tier") or "Standard"
                content = row.get("Mensaje_Cliente") or row.get("content") or ""
                ref_id = row.get("ID") or row.get("external_reference_id") or f"REF-{processed+1}"

                if not content.strip():
                    continue

                try:
                    payload = InteractionCreate(
                        customer_external_id=cust_id,
                        customerName=f"Empresa {cust_id}",
                        tier=tier,
                        source_type=channel,
                        content=content,
                        external_reference_id=ref_id
                    )

                    IngestionPipelineService.process_single_interaction(db, payload, batch_id="cli-batch-ingest")
                    processed += 1
                    if processed % 10 == 0:
                        print(f"  [+] Procesadas {processed} interacciones...")

                except Exception as e:
                    if "duplicada" in str(e).lower():
                        duplicates += 1
                    else:
                        errors += 1
                        print(f"  [!] Error en registro {ref_id}: {e}")

        total_interactions = db.query(Interaction).count()
        total_customers = db.query(Customer).count()
        duration = time.time() - start_time

        print("=" * 70)
        print("   INGESTA MASIVA COMPLETADA CON ÉXITO")
        print(f"   - Procesadas en esta corrida: {processed}")
        print(f"   - Duplicadas ignoradas:       {duplicates}")
        print(f"   - Errores:                    {errors}")
        print(f"   - Tiempo total de ejecución:  {duration:.2f}s")
        print(f"   - Total Interacciones en BD:  {total_interactions}")
        print(f"   - Total Clientes en BD:       {total_customers}")
        print("=" * 70)
        print("\nRecarga el Dashboard en tu navegador (F5 en http://localhost:8000) para ver todos los gráficos y KPIs actualizados.\n")

    finally:
        db.close()


if __name__ == "__main__":
    run_batch_ingest()
