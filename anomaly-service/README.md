# Anomaly Service

FastAPI microservice for UEBA-style anomaly scoring in the Synthetic AI SOC platform.

## Endpoints
- `GET /health/live` – Liveness probe.
- `GET /health/ready` – Readiness probe; reports model readiness/version.
- `GET /metadata` – Basic service metadata.
- `POST /v1/score` – Score a single event payload.
- `POST /v1/score/batch` – Score multiple events in one request.

## Running locally
```bash
cd anomaly-service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Environment
- `ANOMALY_HOST` (default `0.0.0.0`)
- `ANOMALY_PORT` (default `8001`)
- `ANOMALY_MODEL_PATH` (default `models/dev_isolation_forest.pkl`)
- `ANOMALY_FEATURE_STORE_URL` (default `redis://feature-store:6379`)
- `ANOMALY_ALERT_STORE_URL` (default `http://alert-store:8000`)
- `ANOMALY_LOG_LEVEL` (default `INFO`)

The service currently uses a placeholder scorer; wire in a real model by implementing `AnomalyScoringService`.
