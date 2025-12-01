import json
import os
import sys
from typing import Dict, List

import httpx

ANOMALY_URL = os.getenv("ANOMALY_URL", "http://localhost:8001/score")
ALERT_STORE_URL = os.getenv("ALERT_STORE_URL", "http://localhost:8003/alerts")


def score_event(event: Dict, client: httpx.Client) -> Dict:
    resp = client.post(ANOMALY_URL, json={"event": event})
    resp.raise_for_status()
    return resp.json()


def send_to_alert_store(event: Dict, score: Dict, client: httpx.Client) -> None:
    payload = {
        "event": event,
        "score": score.get("score"),
        "threshold": score.get("threshold"),
        "is_anomaly": score.get("is_anomaly"),
        "model": score.get("model", "unknown"),
        "mitre_tactics": event.get("mitre_tactics", []),
        "mitre_techniques": event.get("mitre_techniques", []),
    }
    client.post(ALERT_STORE_URL, json=payload, timeout=5).raise_for_status()


def main() -> None:
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
                send_to_alert_store(event, result, client)
                sys.stdout.write(json.dumps({"event": event, "score": result}) + "\n")
                sys.stdout.flush()
            except Exception as exc:
                sys.stderr.write(f"Error scoring or storing event: {exc}\n")


if __name__ == "__main__":
    main()
