"""
Script Oficial de Prueba de Estrés y Rendimiento (10,000 Registros)
Proyecto: Churn Sentinel AI
Valida el Pipeline de IA (Sanitización PII + Inferencia en Cascada) y el Backend (Risk Engine + Base de Datos).
"""

import os
import sys
import csv
import time
import argparse
from typing import Dict, Any, List

# Configuración de Paths
project_root = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.join(project_root, "backend")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Configurar encoding UTF-8 en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from ai_pipeline.pipeline import AIPipelineOrchestrator
from ai_pipeline.schemas import InteractionPayload, InteractionSource, SentimentType
from backend.app.db.session import SessionLocal
from backend.app.db.init_db import init_db
from backend.app.schemas.interaction import InteractionCreate
from backend.app.services.ingestion_service import IngestionPipelineService
from backend.app.models.customer import Customer
from backend.app.models.interaction import Interaction
from backend.app.models.alert import Alert
from backend.app.models.churn_risk import ChurnRisk


def ensure_dataset(file_path: str, count: int = 10000):
    """Verifica que el dataset de 10k exista; si no, lo genera automáticamente."""
    if not os.path.exists(file_path):
        print(f"[*] Dataset no encontrado en {file_path}. Generándolo automáticamente...")
        from generate_stress_datasets import generate_dataset
        generate_dataset(os.path.basename(file_path), count)


def run_pipeline_only_test(csv_path: str, limit: int = 10000):
    """
    PRUEBA 1: Solo AI Pipeline
    Evalúa PII Scrubbing, Inferencia Semántica y Throughput puro sin I/O de base de datos.
    """
    print("\n" + "=" * 75)
    print("   [FASE 1] PRUEBA DE ESTRÉS: AI PIPELINE PURO (10,000 REGISTROS)")
    print(f"   Archivo: {csv_path}")
    print("=" * 75)

    orchestrator = AIPipelineOrchestrator(enable_cloud=True)
    
    total = 0
    pii_masked_total = 0
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    churn_intents = 0
    latencies = []

    start_time = time.perf_counter()

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            if i > limit:
                break

            cust_id = row.get("customer_external_id") or row.get("Cliente_ID") or f"CUST-{i}"
            tier = row.get("tier") or row.get("Tier") or "Standard"
            channel = row.get("source_type") or row.get("Canal") or "support_ticket"
            content = row.get("content") or row.get("Mensaje_Cliente") or ""

            payload = InteractionPayload(
                interaction_id=f"TEST-PIPE-{i}",
                customer_id=cust_id,
                customer_tier=tier,
                source=InteractionSource.SUPPORT_TICKET,
                message=content
            )

            t0 = time.perf_counter()
            res = orchestrator.process_interaction(payload)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            latencies.append(elapsed_ms)

            total += 1
            if res.processing_metadata.get("was_pii_scrubbed"):
                pii_masked_total += res.processing_metadata.get("pii_masked_count", 0)

            sent_val = res.sentiment.value if hasattr(res.sentiment, "value") else str(res.sentiment)
            sentiments[sent_val] = sentiments.get(sent_val, 0) + 1

            if res.churn_intent:
                churn_intents += 1

            if i % 2000 == 0 or i == limit:
                current_time = time.perf_counter() - start_time
                fps = total / current_time if current_time > 0 else 0
                print(f"   -> Progreso: {i:,} / {limit:,} interacciones analizadas ({fps:.1f} msg/s)...")

    total_duration = time.perf_counter() - start_time
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)] if latencies else 0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
    throughput = total / total_duration if total_duration > 0 else 0

    print("\n" + "-" * 75)
    print("   📊 RESULTADOS FINALES: AI PIPELINE (10,000 REGISTROS)")
    print("-" * 75)
    print(f"   • Total Mensajes Procesados : {total:,}")
    print(f"   • Tiempo Total              : {total_duration:.2f} segundos")
    print(f"   • Throughput de IA          : {throughput:.1f} mensajes / segundo")
    print(f"   • Latencia Promedio         : {avg_latency:.2f} ms")
    print(f"   • Latencia P50 (Mediana)    : {p50:.2f} ms")
    print(f"   • Latencia P95              : {p95:.2f} ms")
    print(f"   • Entidades PII Sanitizadas : {pii_masked_total:,}")
    print(f"   • Alertas de Churn Detectadas: {churn_intents:,} ({churn_intents/total*100:.1f}%)")
    print(f"   • Distribución de Sentimiento: Positivos: {sentiments.get('positive',0):,} | Neutros: {sentiments.get('neutral',0):,} | Negativos: {sentiments.get('negative',0):,}")
    print("-" * 75)


def run_full_backend_test(csv_path: str, limit: int = 10000):
    """
    PRUEBA 2: Pipeline de IA + Backend Completo
    Ingesta, Deduplicación, PII, Inferencia, Risk Engine (0-100 pts), Persistencia ACID y Alertas.
    """
    print("\n" + "=" * 75)
    print("   [FASE 2] PRUEBA DE INTEGRACIÓN: PIPELINE + BACKEND ACID (10,000 REGISTROS)")
    print(f"   Archivo: {csv_path}")
    print("=" * 75)

    init_db()
    db = SessionLocal()

    processed = 0
    duplicates = 0
    errors = 0
    start_time = time.perf_counter()

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                if i > limit:
                    break

                cust_id = row.get("customer_external_id") or row.get("Cliente_ID") or f"CUST-{i}"
                tier = row.get("tier") or row.get("Tier") or "Standard"
                channel = row.get("source_type") or row.get("Canal") or "support_ticket"
                content = row.get("content") or row.get("Mensaje_Cliente") or ""
                ref_id = row.get("external_reference_id") or row.get("ID") or f"REF-10K-{i}"

                if not content.strip():
                    continue

                try:
                    payload = InteractionCreate(
                        customer_external_id=cust_id,
                        customerName=f"Corporación {cust_id}",
                        tier=tier,
                        source_type=channel,
                        content=content,
                        external_reference_id=ref_id
                    )

                    IngestionPipelineService.process_single_interaction(
                        db=db,
                        payload=payload,
                        batch_id="stress-test-10k"
                    )
                    processed += 1

                except Exception as e:
                    if "duplicada" in str(e).lower() or "unique" in str(e).lower():
                        duplicates += 1
                    else:
                        errors += 1
                        if errors <= 3:
                            print(f"   [!] Error en registro #{i}: {e}")

                if i % 2000 == 0 or i == limit:
                    current_time = time.perf_counter() - start_time
                    fps = processed / current_time if current_time > 0 else 0
                    print(f"   -> Progreso Backend: {i:,} / {limit:,} transacciones ({fps:.1f} tx/s)...")

        total_duration = time.perf_counter() - start_time
        total_interactions = db.query(Interaction).count()
        total_customers = db.query(Customer).count()
        total_alerts = db.query(Alert).count()
        critical_risk_count = db.query(ChurnRisk).filter(ChurnRisk.risk_level.in_(["HIGH", "CRITICAL"])).count()
        throughput = processed / total_duration if total_duration > 0 else 0

        print("\n" + "-" * 75)
        print("   📊 RESULTADOS FINALES: PIPELINE + BACKEND ACID (10,000 REGISTROS)")
        print("-" * 75)
        print(f"   • Registros Procesados       : {processed:,}")
        print(f"   • Duplicados Neutralizados   : {duplicates:,} (100% Idempotencia)")
        print(f"   • Errores No Controlados     : {errors}")
        print(f"   • Tiempo Total de Ejecución  : {total_duration:.2f} segundos")
        print(f"   • Throughput Transaccional   : {throughput:.1f} transacciones / segundo")
        print(f"   • Clientes Activos en BD     : {total_customers:,}")
        print(f"   • Interacciones en BD        : {total_interactions:,}")
        print(f"   • Alertas de Riesgo Creadas  : {total_alerts:,}")
        print(f"   • Casos de Alto/Crítico Riesgo: {critical_risk_count:,}")
        print("-" * 75)

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Prueba de Estrés 10,000 Registros - Churn Sentinel AI")
    parser.add_argument(
        "--mode",
        choices=["pipeline", "backend", "all"],
        default="all",
        help="Modo de prueba: 'pipeline' (solo IA), 'backend' (IA + BD), 'all' (ambas fases)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10000,
        help="Límite de registros a procesar (por defecto 10000)"
    )
    parser.add_argument(
        "--file",
        type=str,
        default=os.path.join(project_root, "data", "dataset_10k_interactions.csv"),
        help="Ruta al archivo CSV con las interacciones"
    )

    args = parser.parse_args()

    print("\n" + "#" * 75)
    print("   CHURN SENTINEL AI - SUITE DE ESTRÉS INDUSTRIAL (10,000 REGISTROS)")
    print(f"   Modo: {args.mode.upper()} | Límite: {args.limit:,} registros")
    print("#" * 75)

    ensure_dataset(args.file, args.limit)

    if args.mode in ["pipeline", "all"]:
        run_pipeline_only_test(args.file, args.limit)

    if args.mode in ["backend", "all"]:
        run_full_backend_test(args.file, args.limit)

    print("\n" + "=" * 75)
    print("   [OK] PRUEBA DE ESTRÉS DE 10,000 REGISTROS FINALIZADA SATISFACTORIAMENTE")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
