import json
import os
import sys
from typing import Dict, List, Optional

import httpx

ANOMALY_URL = os.getenv("ANOMALY_URL", "http://localhost:8001/score")
TRIAGE_URL = os.getenv("TRIAGE_URL", "http://localhost:8002/triage")
ALERT_STORE_URL = os.getenv("ALERT_STORE_URL", "http://localhost:8003/alerts/")


def score_event(event: Dict, client: httpx.Client) -> Dict:
    resp = client.post(ANOMALY_URL, json={"event": event})
    resp.raise_for_status()
    return resp.json()


def triage_event(event: Dict, score_result: Dict, client: httpx.Client) -> Dict:
    """Call LLM service to triage the anomaly."""
    payload = {
        "event": event,
        "anomaly_score": score_result.get("score", 0.0),
        "model": score_result.get("model", "unknown"),
    }
    try:
        resp = client.post(TRIAGE_URL, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        sys.stderr.write(f"Triage failed: {exc}\n")
        # Return fallback triage data
        return {
            "category": "Uncategorized",
            "severity": "medium", # Default to medium if unknown
            "confidence": 0.0,
            "summary": "Triage service unavailable.",
            "mitre_attack": {"tactics": [], "techniques": []},
            "indicators": {},
            "recommended_actions": ["Investigate manually"],
        }


def send_to_alert_store(event: Dict, score: Dict, triage: Dict, client: httpx.Client) -> None:
    # Map triage response to AlertCreate schema
    mitre = triage.get("mitre_attack", {})
    
    payload = {
        "source": "synthetic-ai-soc",
        "category": triage.get("category", "Uncategorized"),
        "severity": triage.get("severity", "low"),
        "confidence": triage.get("confidence", 0.0),
        "description": triage.get("summary", "No summary available"),
        "raw_event": json.dumps(event),
        "score": score.get("score", 0.0),
        "model": score.get("model", "unknown"),
        "mitre_tactics": mitre.get("tactics", []),
        "mitre_techniques": mitre.get("techniques", []),
        "indicators": triage.get("indicators", {}),
        "recommended_actions": triage.get("recommended_actions", []),
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
                # 1. Score
                score_result = score_event(event, client)
                
                # 2. If anomaly, Triage and Store
                if score_result.get("is_anomaly"):
                    triage_result = triage_event(event, score_result, client)
                    send_to_alert_store(event, score_result, triage_result, client)
                    
                    # Output for debugging/logging
                    output = {
                        "event": event,
                        "score": score_result,
                        "triage": triage_result
                    }
                    sys.stdout.write(json.dumps(output) + "\n")
                    sys.stdout.flush()
                else:
                    # Just output score for normal events
                    sys.stdout.write(json.dumps({"event": event, "score": score_result}) + "\n")
                    sys.stdout.flush()
                    
            except Exception as exc:
                sys.stderr.write(f"Error processing event: {exc}\n")


if __name__ == "__main__":
    main()
