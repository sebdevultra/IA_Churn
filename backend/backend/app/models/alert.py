from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    churn_risk_id = Column(Integer, ForeignKey("churn_risk.id", ondelete="CASCADE"), nullable=False, index=True)
    severity = Column(String(20), default="CRITICAL", nullable=False, index=True)  # CRITICAL, HIGH
    title = Column(String(200), nullable=False)
    reasons = Column(JSON, nullable=False)  # List of textual reasons triggered
    status = Column(String(30), default="NEW", nullable=False, index=True)  # NEW, ACKNOWLEDGED, RESOLVED
    acknowledged_by = Column(String(100), nullable=True)
    resolved_by = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="alerts")
    churn_risk = relationship("ChurnRisk", back_populates="alert")

    def __repr__(self):
        return f"<Alert id={self.id} customer_id={self.customer_id} severity='{self.severity}' status='{self.status}'>"
