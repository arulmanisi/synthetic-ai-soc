import json
import os

import requests


def main():
    base_url = os.getenv("TRIAGE_URL", "http://localhost:8001")
    event = {
        "timestamp": "2025-11-30T00:00:00Z",
        "user": "eve",
        "action": "login_failed",
        "source_ip": "10.0.0.5",
        "attempts": 7,
    }
    payload = {"event": event, "anomaly_score": 0.82, "model": "lof"}
    resp = requests.post(f"{base_url}/triage", json=payload, timeout=5)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))


if __name__ == "__main__":
    main()
