import json
import os
import sys
from typing import Any, Dict, List

import requests


def fetch_alerts(limit: int = 20) -> List[Dict[str, Any]]:
    url = os.getenv("ALERT_STORE_URL", "http://localhost:8003/alerts")
    resp = requests.get(url, params={"limit": limit}, timeout=5)
    resp.raise_for_status()
    return resp.json()


def main():
    try:
        alerts = fetch_alerts()
        if not alerts:
            print("No alerts found.")
            return
        for alert in alerts:
            print("=" * 60)
            print(f"ID: {alert['id']}  model: {alert['model']}  score: {alert['score']:.3f}")
            print(f"Anomaly: {alert['is_anomaly']}  threshold: {alert['threshold']}")
            mitre_tactics = alert.get("mitre_tactics", [])
            mitre_techniques = alert.get("mitre_techniques", [])
            print(f"MITRE tactics: {', '.join(mitre_tactics) if mitre_tactics else 'none'}")
            print(f"MITRE techniques: {', '.join(mitre_techniques) if mitre_techniques else 'none'}")
            print("Event:")
            print(json.dumps(alert.get("event", {}), indent=2))
    except Exception as exc:
        print(f"Failed to fetch alerts: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
