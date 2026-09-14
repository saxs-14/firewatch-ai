"""
Fire/smoke detection via HSV colour thresholding - a standard, precedented
classical baseline for early fire/smoke detection (predating deep-learning
approaches). Fire: high-saturation red/orange/yellow regions. Smoke: low-
saturation grey regions with moderate brightness and noticeable local
texture variance (to distinguish it from a flat grey wall or sky).
This is an early-warning PROTOTYPE, not a certified detector - see README.
"""
import cv2
import numpy as np

from app.config import settings

FIRE_HSV_RANGES = [
    ((0, 120, 120), (25, 255, 255)),    # red/orange flame
    ((25, 100, 150), (35, 255, 255)),   # yellow flame
]


def _fire_mask(hsv: np.ndarray) -> np.ndarray:
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lo, hi in FIRE_HSV_RANGES:
        mask |= cv2.inRange(hsv, np.array(lo), np.array(hi))
    return mask


def _smoke_mask(hsv: np.ndarray, gray: np.ndarray) -> np.ndarray:
    low_sat = cv2.inRange(hsv, np.array((0, 0, 80)), np.array((180, 60, 220)))
    local_var = cv2.Laplacian(gray, cv2.CV_64F)
    local_var = cv2.convertScaleAbs(local_var)
    _, texture_mask = cv2.threshold(local_var, 4, 255, cv2.THRESH_BINARY)
    texture_mask = cv2.dilate(texture_mask, np.ones((9, 9), np.uint8))
    return cv2.bitwise_and(low_sat, texture_mask)


def analyze_frame(frame: np.ndarray) -> dict:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    fire_mask = _fire_mask(hsv)
    smoke_mask = _smoke_mask(hsv, gray)

    total_px = frame.shape[0] * frame.shape[1]
    fire_pct = round((fire_mask > 0).sum() / total_px * 100, 2)
    smoke_pct = round((smoke_mask > 0).sum() / total_px * 100, 2)

    fire_detected = fire_pct >= settings.sensitivity_pct
    smoke_detected = smoke_pct >= settings.sensitivity_pct * 2  # smoke heuristic is noisier - require more coverage

    confidence = 0.0
    if fire_detected:
        confidence = max(confidence, min(0.4 + fire_pct * 0.03, 0.9))
    if smoke_detected:
        confidence = max(confidence, min(0.25 + smoke_pct * 0.015, 0.6))

    return {
        "fire_detected": bool(fire_detected),
        "smoke_detected": bool(smoke_detected),
        "fire_coverage_pct": fire_pct,
        "smoke_coverage_pct": smoke_pct,
        "confidence": round(confidence, 2),
    }


def process_video(video_path: str, sample_every_n_frames: int = 15) -> dict:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    frame_no = 0
    worst = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_no += 1
        if frame_no % sample_every_n_frames != 0:
            continue
        result = analyze_frame(frame)
        if worst is None or result["confidence"] > worst["confidence"]:
            worst = result

    cap.release()
    return worst or {
        "fire_detected": False, "smoke_detected": False,
        "fire_coverage_pct": 0.0, "smoke_coverage_pct": 0.0, "confidence": 0.0,
    }
