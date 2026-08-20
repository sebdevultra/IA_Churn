from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class FrictionPoint(Base):
    __tablename__ = "friction_points"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # customer_support, product_reliability, pricing, usability, billing, onboarding, performance
    description = Column(String(255), nullable=False)
    severity = Column(String(20), default="medium", nullable=False)  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    interaction = relationship("Interaction", back_populates="frictions")

    def __repr__(self):
        return f"<FrictionPoint id={self.id} category='{self.category}' severity='{self.severity}'>"
