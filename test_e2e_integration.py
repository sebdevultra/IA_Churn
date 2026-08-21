"""
Script de validación End-to-End para el sistema integrado:
ai_pipeline + Backend (FastAPI + Risk Engine) + Frontend Endpoints.
"""
import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.join(project_root, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.main import app
from backend.app.services.ai_service import get_ai_provider, AIContextInput
from backend.app.services.ingestion_service import IngestionPipelineService
from backend.app.schemas.interaction import InteractionCreate
from backend.app.db.session import SessionLocal
from backend.app.db.init_db import init_db
from fastapi.testclient import TestClient


def run_e2e_validation():
    print("\n" + "=" * 65)
    print("   INICIANDO SUITE DE VALIDACION INTEGRAL END-TO-END")
    print("=" * 65 + "\n")

    # 1. Base de Datos
    print("[1/5] Inicializando Base de Datos Relacional...")
    init_db()
    print("      [OK] Esquema y clientes semilla verificados.")

    # 2. AI Pipeline Integration
    print("\n[2/5] Probando AI Pipeline (PII Scrubbing + Inferencia en Cascada)...")
    ai = get_ai_provider()
    context = AIContextInput(customer_id="CUST-1001", tier="Enterprise", recent_interactions_count=2)
    sample_text = "Exijo la cancelacion inmediata de nuestro contrato por pesimo soporte. Contactar a admin@enterprise.com con el CVC 458."
    output, p_tok, c_tok, engine = ai.analyze_interaction(sample_text, context)

    print(f"      [OK] Motor AI utilizado: {engine}")
    print(f"      [OK] Sentimiento detectado: {output.sentiment}")
    print(f"      [OK] Emocion predominante: {output.emotion}")
    print(f"      [OK] Intencion de Churn: {output.churn_intent}")
    print(f"      [OK] Fricciones identificadas: {[f.category for f in output.friction_points]}")
    print(f"      [OK] Evidencia semantica: {output.evidence}")

    assert output.sentiment == "negative", "El sentimiento debió ser clasificado como negative"
    assert output.churn_intent is True, "Debió detectarse churn intent ante 'cancelacion'"

    # 3. Pipeline de Ingesta & Motor de Riesgo Determinista
    print("\n[3/5] Probando Pipeline de Ingesta Completo y Deterministic Risk Engine...")
    db = SessionLocal()
    payload = InteractionCreate(
        customer_external_id="CUST-CORP-99",
        content="Llevamos 4 dias esperando respuesta al ticket #9901 y el servidor sigue caido. Si no arreglan esto nos pasamos a la competencia.",
        tier="Enterprise",
        customerName="Corporacion Global Tech"
    )

    interaction = IngestionPipelineService.process_single_interaction(db, payload)
    print(f"      [OK] Interaccion creada: #{interaction.id} ({interaction.status})")
    print(f"      [OK] Risk Score Calculado: {interaction.churn_risk.risk_score} / 100 ({interaction.churn_risk.risk_level})")
    print(f"      [OK] Desglose de Factores: {len(interaction.churn_risk.score_breakdown)} reglas aplicadas")
    print(f"      [OK] Alerta Transaccional Disparada: {len(interaction.customer.alerts) > 0}")

    assert interaction.churn_risk.risk_score >= 60, "El score de riesgo debe ser Alto o Crítico (>= 60)"
    db.close()

    # 4. Pruebas de Endpoints de FastAPI (Consola & Dashboard)
    print("\n[4/5] Probando Endpoints REST para el Frontend...")
    with TestClient(app) as client:
        # A. KPIs
        r_kpi = client.get("/api/analytics/kpis")
        assert r_kpi.status_code == 200, f"Error en KPIs: {r_kpi.text}"
        kpis = r_kpi.json()["data"]
        print(f"      [OK] GET /api/analytics/kpis -> Total: {kpis['totalInteractions']}, NPS: {kpis['predictiveNps']}, Criticos: {kpis['criticalRiskCount']}")

        # B. Tendencia Temporal
        r_trend = client.get("/api/analytics/sentiment-trend")
        assert r_trend.status_code == 200
        trend = r_trend.json()["data"]
        print(f"      [OK] GET /api/analytics/sentiment-trend -> {len(trend)} puntos de evolucion temporal")

        # C. Distribucion de Fricciones
        r_fric = client.get("/api/analytics/friction-distribution")
        assert r_fric.status_code == 200
        fric = r_fric.json()["data"]
        print(f"      [OK] GET /api/analytics/friction-distribution -> {fric}")

        # D. Casos de Alto Riesgo
        r_cases = client.get("/api/churn/high-risk")
        assert r_cases.status_code == 200
        cases = r_cases.json()["data"]
        print(f"      [OK] GET /api/churn/high-risk -> {len(cases)} casos en bandeja")

        # E. Simulador en Vivo (Testbed POST)
        r_sim = client.post("/api/interactions", json={
            "customerName": "Fintech Alpha",
            "tier": "Enterprise",
            "text": "Excelente soporte y gran estabilidad, felicidades al equipo.",
            "aiEngine": "cloud_gemini"
        })
        assert r_sim.status_code == 201, f"Error en simulador: {r_sim.text}"
        sim_data = r_sim.json()["data"]
        print(f"      [OK] POST /api/interactions (Simulador) -> Score: {sim_data['riskScore']} pts | Emocion: {sim_data['emotion']}")

        # F. Actualizacion de Estado de Alerta (PATCH)
        if cases:
            first_case_id = cases[0]["id"]
            r_patch = client.patch(f"/api/alerts/{first_case_id}", json={
                "status": "RESOLVED",
                "resolution_notes": "Contacto telefonico exitoso con el cliente."
            })
            assert r_patch.status_code == 200
            print(f"      [OK] PATCH /api/alerts/{first_case_id} -> Estado actualizado a RESOLVED")

    # 5. Servido del Frontend
    print("\n[5/5] Verificando Servido de Archivos Estaticos del Frontend...")
    with TestClient(app) as client:
        r_home = client.get("/")
        assert r_home.status_code == 200
        assert "<title>" in r_home.text or "html" in r_home.text.lower()
        print("      [OK] GET / -> index.html del Frontend cargado exitosamente.")

        r_js = client.get("/js/app.js")
        assert r_js.status_code == 200
        print("      [OK] GET /js/app.js -> Modulo JavaScript entregado.")

        r_css = client.get("/css/main.css")
        assert r_css.status_code == 200
        print("      [OK] GET /css/main.css -> Estilos CSS entregados.")

    print("\n" + "=" * 65)
    print("   TODAS LAS PRUEBAS END-TO-END PASARON SATISFACTORIAMENTE (100%)")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_e2e_validation()
