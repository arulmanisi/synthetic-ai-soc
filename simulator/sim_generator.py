import json
import random
import sys
import time
from datetime import datetime, timezone
from typing import Dict

USERS = ["alice", "bob", "charlie", "dana", "eve"]
APPS = ["crm", "erp", "vpn", "sshd", "s3"]
HOSTS = ["host-1", "host-2", "host-3"]
ACTIONS = ["login", "logout", "file_access", "upload", "download"]


def generate_event() -> Dict:
    user = random.choice(USERS)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "host": random.choice(HOSTS),
        "app": random.choice(APPS),
        "action": random.choice(ACTIONS),
        "bytes": random.randint(100, 50000),
        "success": random.random() > 0.05,
    }
    # Inject simple anomalies
    if random.random() < 0.05:
        event["bytes"] = random.randint(200000, 500000)
        event["action"] = "exfiltration"
    return event


def main() -> None:
    delay = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    while True:
        evt = generate_event()
        sys.stdout.write(json.dumps(evt) + "\n")
        sys.stdout.flush()
        time.sleep(delay)


if __name__ == "__main__":
    main()
