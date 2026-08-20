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
            logger.info("Database is empty. Seeding initial customers...")
            for cust_data in INITIAL_CUSTOMERS:
                customer = Customer(
                    external_id=cust_data["external_id"],
                    name=cust_data["name"],
                    email=cust_data["email"],
                    tier=cust_data["tier"],
                    historical_summary=cust_data["historical_summary"],
                    current_risk_score=cust_data["current_risk_score"],
                    current_risk_level=cust_data["current_risk_level"],
                    last_interaction_at=datetime.utcnow() - timedelta(days=2)
                )
                db.add(customer)
            db.commit()
            logger.info(f"Successfully seeded {len(INITIAL_CUSTOMERS)} baseline customers.")
        else:
            logger.info(f"Database already contains {existing_count} customers. Skipping initial seed.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during init_db: {str(e)}")
        raise
    finally:
        if close_after:
            db.close()
