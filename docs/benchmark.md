# Anomaly Service Benchmark (local)

Command:
```bash
# Terminal 1
cd anomaly-service
source .venv/bin/activate
uvicorn app:app --host 127.0.0.1 --port 8001 --log-level warning

# Terminal 2 (repo root)
anomaly-service/.venv/bin/python scripts/benchmark_model.py
```

Results (2025-11-29, local IsolationForest baseline):
- Precision: 0.372
- Recall: 0.700
- F1: 0.486
- ROC-AUC: 0.566
- Confusion matrix: TN=34, FP=59, FN=15, TP=35

Per-technique metrics (heuristic MITRE tags) — run `scripts/benchmark_model.py` to refresh:
- T1041/T1048 Exfiltration: TBD
- T1110 Brute Force: TBD
- T1071 C2: TBD
- T1021 Lateral Movement: TBD

Notes:
- Benchmark uses synthetic events from `simulator/sim_generator.py` and the `/evaluate` endpoint.
- Threshold is currently 0.5 with contamination at 0.2; tune these or train/load a model to improve precision.***
