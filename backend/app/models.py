from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from datetime import datetime, timezone
from app.database import Base


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id = Column(Integer, primary_key=True)
    source_filename = Column(String)
    fire_detected = Column(Boolean)
    smoke_detected = Column(Boolean)
    fire_coverage_pct = Column(Float)
    smoke_coverage_pct = Column(Float)
    confidence = Column(Float)
    evidence_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
