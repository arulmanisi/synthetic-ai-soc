# Anomaly Service

FastAPI microservice scaffold for anomaly scoring in the Synthetic AI SOC platform.

## Endpoints
- `GET /health` – Liveness.
- `GET /models` – List available model names.
- `POST /score` – Score a JSON event (placeholder returns 0.5).

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
- `ANOMALY_LOG_LEVEL` (default `INFO`)
- `ANOMALY_DEFAULT_MODEL` (default `placeholder-v0`)

## Tests
```bash
cd anomaly-service
pytest
```

The scoring pipeline in `pipelines/scorer.py` is a placeholder; replace with a real model when ready.
