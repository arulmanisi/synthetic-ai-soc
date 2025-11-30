# Synthetic AI SOC Roadmap (MITRE-first, AI-driven)

## Goals
- One-stop open-source project for MITRE ATT&CK simulation, anomaly detection, and LLM triage.
- Deterministic baselines with optional LLM enrichment (guardrails + fallbacks).
- Measurable coverage and per-technique metrics.

## Phases

### Phase 1: Simulator Depth (MITRE coverage)
- Add tactic-specific scenarios with labels: T1110 (brute force), T1048/T1041 (exfil), T1071 (C2), T1021 (lateral movement), T1046/T1083 (discovery), T1059 (exec).
- Parameterize campaigns (intensity, noise, duration) and emit MITRE tags on events.
- Add rare/benign variants to test false-positive resilience.

### Phase 2: Ingestion & Storage
- Add Kafka/Redis ingestion option; keep stdin pipe fallback.
- Implement Alert Store API + DB (SQLite → Postgres) with schema for alerts, scores, MITRE tags, triage summaries.
- Persist scored anomalies from ingestion into Alert Store.

### Phase 3: Models & Evaluation
- Persist/load trained models (IsolationForest/LOF + slots for future models).
- Per-technique evaluation: precision/recall/ROC per MITRE tag; threshold sweeps with reports.
- Add score histograms/anomaly rates to Prometheus metrics; expose `/metrics`.
- Scripted benchmark to compare models (IF vs LOF) with technique filters.

### Phase 4: LLM Triage & Explanations
- Enhance `/triage` to always return MITRE tags and rationale; configurable model choice.
- Add `/explain` endpoint with short RAG-style enrichment (mock/local allowed).
- Rule-first, LLM-second flow with explicit fallbacks and logging of LLM usage.
- Add redaction/guardrails for prompts.

### Phase 5: UI & Observability
- Minimal dashboard: recent alerts, MITRE tags, triage summary, score distributions, health.
- Add Grafana/Prometheus dashboards for latency, error rates, anomaly rate, score histogram.
- Scripts for health checks and smoke tests.

### Phase 6: Packaging & Docs
- Docker/compose for all services (simulator, ingestion, anomaly, alert-store, llm-reasoner, UI).
- Usage guides: end-to-end runbook, MITRE coverage doc auto-generated from mappings.
- Contribution guide for adding new techniques and scenarios.

## Near-term tasks (next iterations)
1) Expand simulator scenarios with T1110, T1048/T1041, T1071, T1021, T1046/T1083, T1059 tags.
2) Build Alert Store API + schema (start with SQLite), persist scored anomalies with MITRE fields.
3) Add per-technique metrics in `benchmark_model.py` and a threshold sweep.
4) Enhance triage response to include MITRE tags and rationale by default; add guardrails.
5) Add a minimal dashboard view for alerts + MITRE + triage summary.
