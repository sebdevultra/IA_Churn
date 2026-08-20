from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    external_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False)
    tier = Column(String(50), default="standard", nullable=False)  # standard, pro, enterprise
    historical_summary = Column(Text, default="", nullable=False)  # Compact AI summary cache
    current_risk_score = Column(Integer, default=0, nullable=False)
    current_risk_level = Column(String(20), default="LOW", nullable=False)
    last_interaction_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    interactions = relationship("Interaction", back_populates="customer", cascade="all, delete-orphan", order_by="desc(Interaction.created_at)")
    churn_records = relationship("ChurnRisk", back_populates="customer", cascade="all, delete-orphan", order_by="desc(ChurnRisk.calculated_at)")
    alerts = relationship("Alert", back_populates="customer", cascade="all, delete-orphan", order_by="desc(Alert.created_at)")

    def __repr__(self):
        return f"<Customer id={self.id} external_id='{self.external_id}' risk_score={self.current_risk_score}>"
