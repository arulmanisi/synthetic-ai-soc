import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


DB_PATH = Path(os.getenv("ALERT_DB_PATH", Path(__file__).parent / "alerts.db"))


class AlertIn(BaseModel):
    event: Dict[str, Any]
    score: float = Field(..., ge=0.0, le=1.0)
    threshold: float = Field(..., ge=0.0, le=1.0)
    is_anomaly: bool
    model: str
    mitre_tactics: Optional[List[str]] = Field(default_factory=list)
    mitre_techniques: Optional[List[str]] = Field(default_factory=list)


class Alert(AlertIn):
    id: int
    created_at: str


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_json TEXT NOT NULL,
            score REAL NOT NULL,
            threshold REAL NOT NULL,
            is_anomaly INTEGER NOT NULL,
            model TEXT NOT NULL,
            mitre_tactics TEXT,
            mitre_techniques TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    return conn


app = FastAPI(title="Alert Store")


@app.on_event("startup")
def startup_event() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    init_db(get_conn())


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/alerts", response_model=Alert)
def create_alert(alert: AlertIn) -> Alert:
    conn = get_conn()
    mitre_tactics = json.dumps(alert.mitre_tactics or [])
    mitre_techniques = json.dumps(alert.mitre_techniques or [])
    cur = conn.execute(
        """
        INSERT INTO alerts (
            event_json, score, threshold, is_anomaly, model, mitre_tactics, mitre_techniques
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            json.dumps(alert.event),
            alert.score,
            alert.threshold,
            1 if alert.is_anomaly else 0,
            alert.model,
            mitre_tactics,
            mitre_techniques,
        ),
    )
    conn.commit()
    alert_id = cur.lastrowid
    row = conn.execute(
        """
        SELECT id, event_json, score, threshold, is_anomaly, model, mitre_tactics, mitre_techniques, created_at
        FROM alerts WHERE id = ?
        """,
        (alert_id,),
    ).fetchone()
    conn.close()
    return _row_to_alert(row)


@app.get("/alerts", response_model=List[Alert])
def list_alerts(limit: int = 100) -> List[Alert]:
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, event_json, score, threshold, is_anomaly, model, mitre_tactics, mitre_techniques, created_at
        FROM alerts
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [_row_to_alert(row) for row in rows]


def _row_to_alert(row: Any) -> Alert:
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    (
        alert_id,
        event_json,
        score,
        threshold,
        is_anomaly,
        model,
        mitre_tactics,
        mitre_techniques,
        created_at,
    ) = row
    return Alert(
        id=alert_id,
        event=json.loads(event_json),
        score=score,
        threshold=threshold,
        is_anomaly=bool(is_anomaly),
        model=model,
        mitre_tactics=json.loads(mitre_tactics or "[]"),
        mitre_techniques=json.loads(mitre_techniques or "[]"),
        created_at=created_at,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.getenv("ALERT_HOST", "0.0.0.0"),
        port=int(os.getenv("ALERT_PORT", "8003")),
        log_level=os.getenv("ALERT_LOG_LEVEL", "info"),
    )
