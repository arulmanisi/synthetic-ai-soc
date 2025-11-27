## Synthetic AI SOC Data Flow (MVP)

```
[Simulator]
    └─ emits synthetic logs/events
        ↓
[Ingestion Layer]
    └─ normalizes & forwards events
        ↓
[Stream Processing]
    └─ feature extraction / enrichment
        ↓
[Feature Store / Embeddings]
    └─ persists feature vectors per entity
        ↓
[Anomaly Service (FastAPI)]
    ├─ loads model (IsolationForest stub)
    ├─ GET /health, /models, /metrics
    └─ POST /score → anomaly score + decision
        ↓
[Alert Store]
    └─ persists alerts + context
        ↓
[LLM Reasoner / RAG]
    └─ summarizes, triages, explains
        ↓
[UI Dashboard]
    └─ surfaces alerts, scores, explanations
```

### How anomaly detection works (current skeleton)
- Stream jobs engineer features per event/entity and push to the feature store.
- Clients call `POST /score` on `anomaly-service` with an event payload and optional model/threshold overrides.
- The service vectorizes features (hashing categorical values), runs an IsolationForest-based scorer, and returns:
  - `score` in [0,1]
  - `threshold` and `is_anomaly` (decision)
  - `model` name
- Metrics are exposed at `/metrics` via Prometheus instrumentation for latency and request counts.

### Next steps to harden
- Persist/load trained model artifacts instead of fitting a baseline on the fly.
- Add feature validation/drift monitors and richer metrics (score histograms, anomaly rate).
- Wire the Alert Store API and LLM Reasoner once anomaly decisions are persisted.
