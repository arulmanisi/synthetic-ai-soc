import json
import sys
from typing import Dict

import httpx

ANOMALY_URL = "http://localhost:8001/score"


def score_event(event: Dict, client: httpx.Client) -> Dict:
    resp = client.post(ANOMALY_URL, json={"event": event})
    resp.raise_for_status()
    return resp.json()


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
                sys.stdout.write(json.dumps({"event": event, "score": result}) + "\n")
                sys.stdout.flush()
            except Exception as exc:
                sys.stderr.write(f"Error scoring event: {exc}\n")


if __name__ == "__main__":
    main()
