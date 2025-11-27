from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_score_endpoint_returns_placeholder_score():
    payload = {"event": {"foo": "bar"}}
    response = client.post("/score", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body["score"] <= 1.0
    assert body["model"] == "isolation-forest"
    assert "threshold" in body
    assert isinstance(body["is_anomaly"], bool)


def test_score_is_deterministic_for_same_payload():
    payload = {"event": {"foo": "bar", "value": 10}}
    scores = []
    for _ in range(3):
        resp = client.post("/score", json=payload)
        assert resp.status_code == 200
        scores.append(resp.json()["score"])
    assert len(set(scores)) == 1


def test_threshold_override():
    payload = {"event": {"key": "value"}, "threshold": 0.0}
    resp = client.post("/score", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_anomaly"] is True


def test_models_endpoint_lists_models():
    response = client.get("/models")
    assert response.status_code == 200
    body = response.json()
    assert "models" in body
    assert "isolation-forest" in body["models"]
    assert "lof" in body["models"]
