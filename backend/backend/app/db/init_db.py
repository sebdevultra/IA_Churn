from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.db.base import Base
from backend.app.db.session import engine, SessionLocal
from backend.app.models.customer import Customer
from backend.app.core.logging import logger


INITIAL_CUSTOMERS = [
    {
        "external_id": "CUST-1001",
        "name": "Acme Global Corp",
        "email": "contact@acmeglobal.com",
        "tier": "enterprise",
        "historical_summary": "Cliente corporativo crítico con historial de incidencias en rendimiento de API y facturación.",
        "current_risk_score": 45,
        "current_risk_level": "MEDIUM"
    },
    {
        "external_id": "CUST-1002",
        "name": "TechStart Inc",
        "email": "support@techstart.io",
        "tier": "pro",
        "historical_summary": "Empresa SaaS en crecimiento. Uso intensivo de soporte con quejas leves sobre tiempos de respuesta.",
        "current_risk_score": 25,
        "current_risk_level": "LOW"
    },
    {
        "external_id": "CUST-1003",
        "name": "BioHealth Solutions",
        "email": "admin@biohealth.org",
        "tier": "enterprise",
        "historical_summary": "Cliente con múltiples escalaciones a nivel directivo debido a fallos recurrentes en sincronización.",
        "current_risk_score": 85,
        "current_risk_level": "CRITICAL"
    },
    {
        "external_id": "CUST-1004",
        "name": "CloudCommerce LLC",
        "email": "ops@cloudcommerce.shop",
        "tier": "standard",
        "historical_summary": "Cliente estándar sin incidencias críticas previas. Alto uso de autoservicio.",
        "current_risk_score": 10,
        "current_risk_level": "LOW"
    },
    {
        "external_id": "CUST-1005",
        "name": "Fintech Nexus",
        "email": "security@fintechnexus.com",
        "tier": "enterprise",
        "historical_summary": "Cliente de sector financiero con quejas sobre lentitud en soporte de fin de semana.",
        "current_risk_score": 65,
        "current_risk_level": "HIGH"
    }
]


INITIAL_INTERACTIONS = [
    {
        "customer_external_id": "CUST-1001",
        "customer_name": "Acme Global Corp",
        "tier": "Enterprise",
        "source_type": "support_ticket",
        "content": "Hemos experimentado intermitencias leves en la sincronización de webhooks durante la noche.",
        "external_reference_id": "INIT-001"
    },
    {
        "customer_external_id": "CUST-1002",
        "customer_name": "TechStart Inc",
        "tier": "Pro",
        "source_type": "chat",
        "content": "El proceso de integración fue rápido y el soporte resolvió nuestras consultas básicas.",
        "external_reference_id": "INIT-002"
    },
    {
        "customer_external_id": "CUST-1003",
        "customer_name": "BioHealth Solutions",
        "tier": "Enterprise",
        "source_type": "support_ticket",
        "content": "Exijo una reunión con el director de cuentas. Se cayó la base de datos y cancelaremos el contrato corporativo si no hay solución hoy.",
        "external_reference_id": "INIT-003"
    },
    {
        "customer_external_id": "CUST-1004",
        "customer_name": "CloudCommerce LLC",
        "tier": "Standard",
        "source_type": "nps_survey",
        "content": "Excelente servicio, la plataforma es muy intuitiva y nos encanta la facilidad de uso.",
        "external_reference_id": "INIT-004"
    },
    {
        "customer_external_id": "CUST-1005",
        "customer_name": "Fintech Nexus",
        "tier": "Enterprise",
        "source_type": "support_ticket",
        "content": "Llevamos más de 48 horas esperando respuesta al ticket de soporte sobre cobro duplicado.",
        "external_reference_id": "INIT-005"
    }
]


def init_db(db: Session = None):
    """
    Initializes database schema and populates base customer registry if empty.
    """
    logger.info("Verifying database schema tables...")
    Base.metadata.create_all(bind=engine)

    close_after = False
    if db is None:
        db = SessionLocal()
        close_after = True

    try:
        existing_count = db.query(Customer).count()
        if existing_count == 0:
            logger.info("Database is empty. Seeding 5 baseline customer interactions...")
            from backend.app.schemas.interaction import InteractionCreate
            from backend.app.services.ingestion_service import IngestionPipelineService

            for it_data in INITIAL_INTERACTIONS:
                payload = InteractionCreate(
                    customer_external_id=it_data["customer_external_id"],
                    customerName=it_data["customer_name"],
                    tier=it_data["tier"],
                    source_type=it_data["source_type"],
                    content=it_data["content"],
                    external_reference_id=it_data["external_reference_id"]
                )
                IngestionPipelineService.process_single_interaction(db, payload, batch_id="bootstrap-seed")

            logger.info(f"Successfully seeded {len(INITIAL_INTERACTIONS)} baseline interactions and customers.")
        else:
            logger.info(f"Database already contains {existing_count} customers. Skipping initial seed.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during init_db: {str(e)}")
        raise
    finally:
        if close_after:
            db.close()
