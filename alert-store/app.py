import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

DB_PATH = Path(os.getenv("ALERT_DB_PATH", Path(__file__).parent / "alerts.db"))


class AlertIn(BaseModel):
    source: str = "synthetic-ai-soc"
    category: str = "Uncategorized"
    severity: str = "low"
    confidence: float = 0.0
    description: str = "No summary available"
    raw_event: Optional[str] = None
    event: Optional[Dict[str, Any]] = None
    score: float = Field(..., ge=0.0, le=1.0)
    threshold: float = Field(..., ge=0.0, le=1.0)
    is_anomaly: bool
    model: str
    mitre_tactics: Optional[List[str]] = Field(default_factory=list)
    mitre_techniques: Optional[List[str]] = Field(default_factory=list)
    indicators: Optional[Dict[str, Any]] = Field(default_factory=dict)
    recommended_actions: Optional[List[str]] = Field(default_factory=list)


class Alert(AlertIn):
    id: int
    created_at: str


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            category TEXT,
            severity TEXT,
            confidence REAL,
            description TEXT,
            event_json TEXT NOT NULL,
            score REAL NOT NULL,
            threshold REAL NOT NULL,
            is_anomaly INTEGER NOT NULL,
            model TEXT NOT NULL,
            mitre_tactics TEXT,
            mitre_techniques TEXT,
            indicators TEXT,
            recommended_actions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


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
    event_json = alert.raw_event or json.dumps(alert.event or {})
    mitre_tactics = json.dumps(alert.mitre_tactics or [])
    mitre_techniques = json.dumps(alert.mitre_techniques or [])
    indicators = json.dumps(alert.indicators or {})
    actions = json.dumps(alert.recommended_actions or [])
    cur = conn.execute(
        """
        INSERT INTO alerts (
            source, category, severity, confidence, description,
            event_json, score, threshold, is_anomaly, model,
            mitre_tactics, mitre_techniques, indicators, recommended_actions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            alert.source,
            alert.category,
            alert.severity,
            alert.confidence,
            alert.description,
            event_json,
            alert.score,
            alert.threshold,
            1 if alert.is_anomaly else 0,
            alert.model,
            mitre_tactics,
            mitre_techniques,
            indicators,
            actions,
        ),
    )
    conn.commit()
    alert_id = cur.lastrowid
    row = conn.execute(
        """
        SELECT * FROM alerts WHERE id = ?
        """,
        (alert_id,),
    ).fetchone()
    conn.close()
    return _row_to_alert(row)


@app.get("/alerts", response_model=List[Alert])
def list_alerts(
    limit: int = 100,
    offset: int = 0,
    severity: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    tactic: Optional[str] = Query(None, description="Filter by MITRE tactic substring"),
    technique: Optional[str] = Query(None, description="Filter by MITRE technique substring"),
    since: Optional[str] = Query(None, description="ISO timestamp to filter created_at >= since"),
) -> List[Alert]:
    conn = get_conn()
    where_clauses = []
    params: List[Any] = []
    if severity:
        where_clauses.append("severity = ?")
        params.append(severity)
    if model:
        where_clauses.append("model = ?")
        params.append(model)
    if tactic:
        where_clauses.append("mitre_tactics LIKE ?")
        params.append(f"%{tactic}%")
    if technique:
        where_clauses.append("mitre_techniques LIKE ?")
        params.append(f"%{technique}%")
    if since:
        where_clauses.append("created_at >= ?")
        params.append(since)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"""
        SELECT * FROM alerts
        {where_sql}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_alert(row) for row in rows]


def _row_to_alert(row: Any) -> Alert:
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    (
        alert_id,
        source,
        category,
        severity,
        confidence,
        description,
        event_json,
        score,
        threshold,
        is_anomaly,
        model,
        mitre_tactics,
        mitre_techniques,
        indicators,
        recommended_actions,
        created_at,
    ) = row
    return Alert(
        id=alert_id,
        source=source,
        category=category,
        severity=severity,
        confidence=confidence,
        description=description,
        event=json.loads(event_json),
        score=score,
        threshold=threshold,
        is_anomaly=bool(is_anomaly),
        model=model,
        mitre_tactics=json.loads(mitre_tactics or "[]"),
        mitre_techniques=json.loads(mitre_techniques or "[]"),
        indicators=json.loads(indicators or "{}"),
        recommended_actions=json.loads(recommended_actions or "[]"),
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
