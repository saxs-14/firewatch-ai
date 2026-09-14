from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AlertEventOut(BaseModel):
    id: int
    source_filename: str
    fire_detected: bool
    smoke_detected: bool
    fire_coverage_pct: float
    smoke_coverage_pct: float
    confidence: float
    evidence_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    total_checks: int
    total_alerts: int
    fire_alerts: int
    smoke_alerts: int
    sensitivity_pct: float
