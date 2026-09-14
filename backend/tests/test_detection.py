import numpy as np
from app.detection import analyze_frame


def test_analyze_frame_no_alert_on_green_frame():
    frame = np.zeros((200, 200, 3), dtype=np.uint8)
    frame[:] = (40, 140, 40)  # BGR green - not fire-coloured
    result = analyze_frame(frame)
    assert result["fire_detected"] is False


def test_analyze_frame_detects_fire_colour():
    frame = np.zeros((200, 200, 3), dtype=np.uint8)
    frame[:] = (0, 100, 255)  # BGR orange/red - fire-like
    result = analyze_frame(frame)
    assert result["fire_detected"] is True
    assert result["confidence"] > 0


def test_analyze_frame_returns_expected_keys():
    frame = np.zeros((200, 200, 3), dtype=np.uint8)
    result = analyze_frame(frame)
    for key in ["fire_detected", "smoke_detected", "fire_coverage_pct", "smoke_coverage_pct", "confidence"]:
        assert key in result
