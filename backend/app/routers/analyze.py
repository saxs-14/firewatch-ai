import glob
import os
import random
import uuid
import cv2
import numpy as np
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AlertEvent
from app.schemas import AlertEventOut
from app.config import settings
from app.detection import analyze_frame, process_video

router = APIRouter(prefix="/api", tags=["analyze"])

DEMO_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "demo")
IMAGE_EXTS = (".jpg", ".jpeg", ".png")
VIDEO_EXTS = (".mp4", ".avi", ".mov")


def _persist(db, filename, result, evidence_path=None):
    event = AlertEvent(
        source_filename=filename, fire_detected=result["fire_detected"],
        smoke_detected=result["smoke_detected"], fire_coverage_pct=result["fire_coverage_pct"],
        smoke_coverage_pct=result["smoke_coverage_pct"], confidence=result["confidence"],
        evidence_path=evidence_path,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.post("/analyze", response_model=AlertEventOut)
async def analyze(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    if len(contents) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext in IMAGE_EXTS:
        img_array = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if frame is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
        result = analyze_frame(frame)
    elif ext in VIDEO_EXTS:
        upload_path = os.path.join(settings.upload_dir, f"{uuid.uuid4().hex[:8]}_{file.filename}")
        with open(upload_path, "wb") as f:
            f.write(contents)
        result = process_video(upload_path)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {ext}")

    return _persist(db, file.filename, result)


@router.post("/analyze/demo", response_model=AlertEventOut)
def analyze_demo(db: Session = Depends(get_db)):
    samples = []
    for ext in IMAGE_EXTS:
        samples += glob.glob(os.path.join(DEMO_DIR, f"*{ext}"))
    if not samples:
        raise HTTPException(status_code=404, detail="No demo images found on server")
    path = random.choice(samples)
    frame = cv2.imread(path)
    result = analyze_frame(frame)
    return _persist(db, os.path.basename(path), result)
