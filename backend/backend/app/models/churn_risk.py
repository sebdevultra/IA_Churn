from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class ChurnRisk(Base):
    __tablename__ = "churn_risk"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    risk_score = Column(Integer, nullable=False)  # 0 to 100
    risk_level = Column(String(20), nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    score_breakdown = Column(JSON, nullable=False)  # Detailed list of factors and weights applied
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    customer = relationship("Customer", back_populates="churn_records")
    interaction = relationship("Interaction", back_populates="churn_risk")
    alert = relationship("Alert", uselist=False, back_populates="churn_risk", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChurnRisk id={self.id} customer_id={self.customer_id} risk_score={self.risk_score} risk_level='{self.risk_level}'>"
