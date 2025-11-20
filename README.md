📘 Synthetic AI SOC

AI-powered Synthetic Security Operations Platform — LLM-driven analyst co-pilot with synthetic telemetry, anomaly detection, and attack simulation.
Zero enterprise data. Fully open-source.

🚀 Overview

Synthetic AI SOC is a modular, open-source platform that simulates enterprise-like telemetry and security attacks, applies ML/UEBA-based anomaly detection, and uses LLMs to generate high-quality analyst insights and triage summaries.

It allows you to demonstrate end-to-end expertise in:

AI/ML for threat detection

UEBA & anomaly modeling

LLM reasoning for SOC analysts

Real-time ingestion & backend architectures

Detection engineering & behavioral security

Full platform/system design

All data is synthetic, generated entirely by the platform’s simulation engine. No enterprise or sensitive data is used.

🏗 Architecture (MVP)
[Synthetic Log Simulator] 
     → [Ingestion Layer] 
     → [Stream Processor] 
     → [Feature Store + Embeddings] 
     → [Anomaly Scoring Service] 
     → [Alert Store] 
     → [LLM Reasoner / RAG] 
     → [Web UI Dashboard]

✨ Key Features (MVP)

Synthetic log generator (auth, process, network, MITRE-style attack sequences)

Real-time ingestion pipeline (Kafka or simple queue fallback)

Online UEBA-style anomaly detection (Isolation Forest + baselines)

Alerts API (FastAPI) + Postgres store

LLM-powered explanation service (RAG + structured incident summaries)

Lightweight React dashboard for viewing alerts

📂 Project Structure
synthetic-ai-soc/
├─ simulator/                 # Synthetic log & attack simulator
├─ ingestion/                 # Producers & connectors
├─ stream-processing/         # Feature extraction jobs
├─ feature-store/             # Redis/Vector embeddings
├─ anomaly-service/           # ML scoring microservice (FastAPI)
├─ llm-reasoner/              # RAG, prompts, LLM explanations
├─ alert-store/               # Postgres schema + API
├─ graph-db/                  # Optional: attack path graph (v1.0+)
├─ ui/                        # React dashboard
├─ infra/                     # Docker/K8s deployment configs
├─ docs/                      # Architecture, threat modeling
└─ scripts/                   # Demo & tooling scripts

🧪 Quickstart (local dev)
docker-compose up --build

# In a separate terminal:
python simulator/sim_generator.py | python ingestion/producer/send_to_kafka.py


Then open:

👉 http://localhost:3000

to view alerts in the dashboard.

🛣 Roadmap
v0.1 (MVP)

Simulator + ingestion

Anomaly detection service

Alerts API

Basic LLM explanations

Minimal UI

v1.0

Graph DB for identity + attack path reasoning

GNN-based behavioral detection

LLM enrichment playbooks

Policy-as-code (YAML) alert rules

v2.0

Plugin ecosystem

Advanced MITRE ATT&CK simulation

Dataset export for ML research

Cloud-native deployment templates

🤝 Contributing

Contributions, ideas, PRs, and issues are welcome.
This project aims to become a useful security research and learning platform for the community.
