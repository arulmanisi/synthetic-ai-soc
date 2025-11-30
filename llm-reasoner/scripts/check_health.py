import os
import sys

import requests


def main():
    url = os.getenv("TRIAGE_URL", "http://localhost:8002/health")
    try:
        resp = requests.get(url, timeout=5)
        print(f"Status: {resp.status_code}")
        print(resp.json())
    except Exception as exc:
        print(f"Health check failed for {url}: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
