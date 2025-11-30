📘 Synthetic AI SOC

AI-powered Synthetic Security Operations Platform — LLM-driven analyst co-pilot with synthetic telemetry, anomaly detection, and attack simulation.
Zero enterprise data. Fully open-source.

🚀 Overview

Synthetic AI SOC is a modular, open-source platform that simulates enterprise-like telemetry and security attacks, applies ML/UEBA-based anomaly detection, and uses LLMs to generate high-quality analyst insights and triage summaries.

It allows you to demonstrate end-to-end expertise in:

- AI/ML for threat detection
- UEBA & anomaly modeling
- LLM reasoning for SOC analysts
- Real-time ingestion & backend architectures
- Detection engineering & behavioral security
- Full platform/system design

All data is synthetic, generated entirely by the platform's simulation engine. No enterprise or sensitive data is used.

🏗 Architecture (MVP)
```
[Synthetic Log Simulator] 
     → [Ingestion Layer] 
     → [Stream Processor] 
     → [Feature Store + Embeddings] 
     → [Anomaly Scoring Service] 
     → [Alert Store] 
     → [LLM Reasoner / RAG] 
     → [Web UI Dashboard]
```

✨ Key Features (MVP)

- **Synthetic log generator** (auth, process, network, MITRE-style attack sequences)
- **Real-time ingestion pipeline** (Kafka or simple queue fallback)
- **ML-based anomaly detection** (Isolation Forest with 74% recall, F1=0.53)
- **Alerts API** (FastAPI) + SQLite/Postgres store
- **LLM-powered explanation service** (RAG + structured incident summaries)
- **React dashboard** for viewing alerts in real-time
- **Model benchmarking** (Precision, Recall, F1, ROC-AUC metrics)

🤖 ML Models

The platform includes multiple anomaly detection models:

| Model | Status | Performance | Use Case |
|-------|--------|-------------|----------|
| **Isolation Forest** | ✅ Default | F1=0.53, Recall=74% | General anomaly detection |
| LOF | Available | F1=0.00 | Experimental |
| One-Class SVM | Available | F1=0.00 | Experimental |
| Ensemble | Available | F1=0.00 | Experimental |

**Isolation Forest** was selected as the default after extensive benchmarking. See `docs/model_config.md` for details.

📂 Project Structure
```
synthetic-ai-soc/
├─ simulator/                 # Synthetic log & attack simulator
├─ ingestion/                 # Producers & connectors
├─ stream-processing/         # Feature extraction jobs
├─ feature-store/             # Redis/Vector embeddings
├─ anomaly-service/           # ML scoring microservice (FastAPI)
├─ llm-reasoner/              # RAG, prompts, LLM explanations
├─ alert-store/               # SQLite/Postgres schema + API
├─ graph-db/                  # Optional: attack path graph (v1.0+)
├─ ui/                        # React dashboard
├─ infra/                     # Docker/K8s deployment configs
├─ docs/                      # Architecture, benchmarks, model config
└─ scripts/                   # Training, benchmarking, demo scripts
```

🧪 Quickstart (local dev)

**Option 1: Docker Compose (Full Stack)**
```bash
docker-compose up --build
```

**Option 2: Local Development**
```bash
# Terminal 1: Start anomaly service
cd anomaly-service
python3 -m uvicorn app:app --reload --port 8001

# Terminal 2: Run simulator and ingestion
python3 simulator/sim_generator.py | python3 ingestion/ingest_and_score.py

# Terminal 3: Start UI (requires Node.js)
cd ui/webapp
npm install
npm run dev
```

Then open: 👉 **http://localhost:3000** to view alerts in the dashboard.

🔬 ML Training & Benchmarking

**Train the model on real data:**
```bash
python3 scripts/train_model.py
```

**Run benchmarks:**
```bash
python3 scripts/benchmark_model.py
```

**Use alternative models:**
```bash
MODEL=lof python3 scripts/benchmark_model.py
```

🤖 LLM Reasoner (triage)
```bash
# Terminal 1: start LLM reasoner
cd llm-reasoner
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
LLM_HOST=127.0.0.1 LLM_PORT=8002 uvicorn service:app --log-level warning

# Terminal 2: health check
TRIAGE_URL=http://127.0.0.1:8002/health python llm-reasoner/scripts/check_health.py

# Terminal 2: exercise triage endpoint (rule-based or OpenAI if OPENAI_API_KEY is set)
TRIAGE_URL=http://127.0.0.1:8002 python llm-reasoner/scripts/test_triage.py
```

🛣 Roadmap

**v0.1 (MVP)** ✅
- ✅ Simulator + ingestion
- ✅ Anomaly detection service (Isolation Forest)
- ✅ Alerts API
- ✅ ML benchmarking framework
- ✅ React UI dashboard
- 🚧 LLM explanations (basic placeholder)

**v1.0**
- Graph DB for identity + attack path reasoning
- GNN-based behavioral detection
- LLM enrichment playbooks
- Policy-as-code (YAML) alert rules

**v2.0**
- Plugin ecosystem
- Advanced MITRE ATT&CK simulation
- Dataset export for ML research
- Cloud-native deployment templates

📊 Performance Metrics

Current anomaly detection performance (Isolation Forest):
- **Precision**: 41.6%
- **Recall**: 74%
- **F1 Score**: 0.53
- **ROC-AUC**: 0.70

See `docs/model_comparison.md` for detailed benchmarks.

🤝 Contributing

Contributions, ideas, PRs, and issues are welcome.
This project aims to become a useful security research and learning platform for the community.

📚 Documentation

- `docs/architecture.md` - System architecture
- `docs/model_config.md` - ML model configuration
- `docs/model_comparison.md` - Model benchmarking results
- `docs/ml_deep_dive.md` - ML implementation details
