import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict

import httpx

ANOMALY_URL = "http://localhost:8001/score"
DB_PATH = Path(__file__).resolve().parent / "anomalies.db"


def score_event(event: Dict, client: httpx.Client) -> Dict:
    resp = client.post(ANOMALY_URL, json={"event": event})
    resp.raise_for_status()
    return resp.json()


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_json TEXT NOT NULL,
            score REAL NOT NULL,
            threshold REAL NOT NULL,
            is_anomaly INTEGER NOT NULL,
            model TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def store_result(conn: sqlite3.Connection, event: Dict, score: Dict) -> None:
    conn.execute(
        """
        INSERT INTO anomalies (event_json, score, threshold, is_anomaly, model)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            json.dumps(event),
            float(score.get("score", 0.0)),
            float(score.get("threshold", 0.0)),
            1 if score.get("is_anomaly") else 0,
            score.get("model", "unknown"),
        ),
    )
    conn.commit()


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    with httpx.Client(timeout=5.0) as client:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                sys.stderr.write(f"Skipping invalid JSON: {line}\n")
                continue
            try:
                result = score_event(event, client)
                store_result(conn, event, result)
                sys.stdout.write(json.dumps({"event": event, "score": result}) + "\n")
                sys.stdout.flush()
            except Exception as exc:
                sys.stderr.write(f"Error scoring event: {exc}\n")

    conn.close()


if __name__ == "__main__":
    main()
