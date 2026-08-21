from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from backend.app.db.base import Base


class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(String(64), nullable=False, index=True)
    step = Column(String(50), nullable=False, index=True)  # INGESTION, AI_ANALYSIS, RISK_ENGINE, ALERT_ENGINE
    status = Column(String(20), nullable=False, index=True)  # SUCCESS, ERROR, WARNING
    records_processed = Column(Integer, default=0, nullable=False)
    duplicates_count = Column(Integer, default=0, nullable=False)
    errors_count = Column(Integer, default=0, nullable=False)
    duration_ms = Column(Float, default=0.0, nullable=False)
    details = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<ProcessingLog id={self.id} batch_id='{self.batch_id}' step='{self.step}' status='{self.status}'>"
