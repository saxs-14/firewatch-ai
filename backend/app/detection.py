"""
Fire/smoke detection combines two independent signals and alerts on either:
1. HSV colour/texture heuristic (fast, works on any image, catches obvious
   colour-block cases) - the original baseline, still used for the
   fire/smoke coverage-percentage stats.
2. A trained MobileNetV2 classifier (fire/neutral/smoke, transfer learning
   on the DeepQuestAI Fire-Smoke-Dataset, 94.8% held-out validation
   accuracy) - more accurate on real photos/frames.
Alerting on either signal avoids a case the trained model wasn't confident
on being silently missed, and vice versa. This is an early-warning
PROTOTYPE, not a certified detector - see README.
"""
import os

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from app.config import settings

FIRE_HSV_RANGES = [
    ((0, 120, 120), (25, 255, 255)),    # red/orange flame
    ((25, 100, 150), (35, 255, 255)),   # yellow flame
]

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_model", "firewatch_classifier.pt")
_MODEL_CLASSES = ["fire", "neutral", "smoke"]
_TRANSFORM = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

_model = torch.jit.load(_MODEL_PATH, map_location="cpu")
_model.eval()


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


def _model_predict(frame: np.ndarray):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    tensor = _TRANSFORM(Image.fromarray(rgb)).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(_model(tensor), dim=1)[0]
    idx = int(torch.argmax(probs))
    return _MODEL_CLASSES[idx], float(probs[idx])


def analyze_frame(frame: np.ndarray) -> dict:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    fire_mask = _fire_mask(hsv)
    smoke_mask = _smoke_mask(hsv, gray)

    total_px = frame.shape[0] * frame.shape[1]
    fire_pct = round((fire_mask > 0).sum() / total_px * 100, 2)
    smoke_pct = round((smoke_mask > 0).sum() / total_px * 100, 2)

    heuristic_fire = fire_pct >= settings.sensitivity_pct
    heuristic_smoke = smoke_pct >= settings.sensitivity_pct * 2  # smoke heuristic is noisier - require more coverage

    predicted_class, model_conf = _model_predict(frame)
    model_fire = predicted_class == "fire"
    model_smoke = predicted_class == "smoke"

    fire_detected = heuristic_fire or model_fire
    smoke_detected = heuristic_smoke or model_smoke

    confidence = 0.0
    if fire_detected:
        confidence = max(confidence, min(0.4 + fire_pct * 0.03, 0.9), model_conf if model_fire else 0.0)
    if smoke_detected:
        confidence = max(confidence, min(0.25 + smoke_pct * 0.015, 0.6), model_conf if model_smoke else 0.0)

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
