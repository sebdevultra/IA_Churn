from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class SentimentAnalysis(Base):
    __tablename__ = "sentiment_analysis"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    sentiment = Column(String(20), nullable=False, index=True)  # positive, neutral, negative
    emotion = Column(String(50), nullable=False, index=True)    # frustration, anger, joy, satisfaction, etc.
    churn_intent = Column(Boolean, default=False, nullable=False, index=True)
    confidence = Column(Float, nullable=False)                  # 0.0 - 1.0
    evidence = Column(JSON, default=list, nullable=False)       # List of quotes/signals
    raw_llm_response = Column(JSON, nullable=True)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    model_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    interaction = relationship("Interaction", back_populates="sentiment")

    def __repr__(self):
        return f"<SentimentAnalysis id={self.id} sentiment='{self.sentiment}' emotion='{self.emotion}' churn_intent={self.churn_intent}>"
