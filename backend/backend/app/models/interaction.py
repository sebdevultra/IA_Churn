from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # support_ticket, review, survey, chat
    content = Column(Text, nullable=False)
    interaction_hash = Column(String(64), unique=True, index=True, nullable=False)  # SHA-256 for deduplication
    external_reference_id = Column(String(100), nullable=True)
    status = Column(String(50), default="PENDING_AI_ANALYSIS", nullable=False, index=True)  # PENDING_AI_ANALYSIS, PROCESSING, PROCESSED, FAILED, RETRYING
    retry_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="interactions")
    sentiment = relationship("SentimentAnalysis", uselist=False, back_populates="interaction", cascade="all, delete-orphan")
    frictions = relationship("FrictionPoint", back_populates="interaction", cascade="all, delete-orphan")
    churn_risk = relationship("ChurnRisk", uselist=False, back_populates="interaction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Interaction id={self.id} customer_id={self.customer_id} status='{self.status}'>"
