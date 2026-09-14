import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models import AlertEvent
from app.schemas import AlertEventOut, DashboardSummary
from app.config import settings

router = APIRouter(prefix="/api", tags=["events"])


@router.get("/events", response_model=List[AlertEventOut])
def list_events(limit: int = 200, db: Session = Depends(get_db)):
    return db.query(AlertEvent).order_by(AlertEvent.created_at.desc()).limit(limit).all()


@router.get("/events/export")
def export_events(db: Session = Depends(get_db)):
    events = db.query(AlertEvent).order_by(AlertEvent.created_at.desc()).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "filename", "fire", "smoke", "fire_pct", "smoke_pct", "confidence", "created_at"])
    for e in events:
        writer.writerow([e.id, e.source_filename, e.fire_detected, e.smoke_detected, e.fire_coverage_pct, e.smoke_coverage_pct, e.confidence, e.created_at])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=firewatch_events.csv"},
    )


@router.get("/dashboard/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    total_checks = db.query(func.count(AlertEvent.id)).scalar() or 0
    fire_alerts = db.query(func.count(AlertEvent.id)).filter(AlertEvent.fire_detected == True).scalar() or 0  # noqa: E712
    smoke_alerts = db.query(func.count(AlertEvent.id)).filter(AlertEvent.smoke_detected == True).scalar() or 0  # noqa: E712
    total_alerts = db.query(func.count(AlertEvent.id)).filter(
        (AlertEvent.fire_detected == True) | (AlertEvent.smoke_detected == True)  # noqa: E712
    ).scalar() or 0
    return DashboardSummary(
        total_checks=total_checks, total_alerts=total_alerts,
        fire_alerts=fire_alerts, smoke_alerts=smoke_alerts,
        sensitivity_pct=settings.sensitivity_pct,
    )
