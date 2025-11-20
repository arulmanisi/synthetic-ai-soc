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
    assert body["score"] == 0.5
    assert body["model"] == "placeholder-v0"


def test_models_endpoint_lists_models():
    response = client.get("/models")
    assert response.status_code == 200
    body = response.json()
    assert "models" in body
    assert "placeholder-v0" in body["models"]
