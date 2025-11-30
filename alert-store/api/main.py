from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from schema.models import Base, Alert, AlertCreate, AlertRead

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./alerts.db" # Use SQLite for MVP, can switch to Postgres later
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Alert Store API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/alerts/", response_model=AlertRead)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    db_alert = Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@app.get("/alerts/", response_model=List[AlertRead])
def read_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(Alert).offset(skip).limit(limit).all()
    return alerts

@app.get("/health")
def health():
    return {"status": "ok"}
