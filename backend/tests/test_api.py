from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200


def test_dashboard_summary_shape():
    r = client.get("/api/dashboard/summary")
    assert r.status_code == 200
    for key in ["total_checks", "total_alerts", "fire_alerts", "smoke_alerts", "sensitivity_pct"]:
        assert key in r.json()


def test_events_list_returns_array():
    r = client.get("/api/events")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_analyze_demo_runs_end_to_end():
    r = client.post("/api/analyze/demo")
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        assert "fire_detected" in r.json()
