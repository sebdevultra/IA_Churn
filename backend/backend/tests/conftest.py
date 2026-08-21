import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.models.customer import Customer

# Use SQLite in-memory with StaticPool so all sessions share the exact same connection & tables
engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db_session():
    """Creates tables and seeds baseline customers for each test."""
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    try:
        # Seed baseline test customers
        cust1 = Customer(
            external_id="CUST-TEST-01",
            name="Test Enterprise Customer",
            email="test1@enterprise.com",
            tier="enterprise",
            historical_summary="Cliente corporativo previo",
            current_risk_score=20,
            current_risk_level="LOW"
        )
        cust2 = Customer(
            external_id="CUST-TEST-02",
            name="Test Standard Customer",
            email="test2@standard.com",
            tier="standard",
            historical_summary="",
            current_risk_score=0,
            current_risk_level="LOW"
        )
        db.add_all([cust1, cust2])
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient overriding get_db with the test database session."""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
