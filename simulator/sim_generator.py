import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from typing import Dict

USERS = ["alice", "bob", "charlie", "dana", "eve"]
APPS = ["crm", "erp", "vpn", "sshd", "s3"]
HOSTS = ["host-1", "host-2", "host-3"]
ACTIONS = ["login", "logout", "file_access", "upload", "download"]
ANOMALY_RATE_DEFAULT = 0.2
MITRE_ACTION_MAP = {
    "login": {"tactics": ["Initial Access", "Credential Access"], "techniques": ["T1078"]},
    "login_failed": {"tactics": ["Credential Access"], "techniques": ["T1110"]},
    "file_access": {"tactics": ["Exfiltration"], "techniques": ["T1048"]},
    "exfiltration": {"tactics": ["Exfiltration"], "techniques": ["T1041"]},
    "process_exec": {"tactics": ["Execution"], "techniques": ["T1059"]},
    "network_connect": {"tactics": ["Command and Control"], "techniques": ["T1071"]},
}


def generate_event() -> Dict:
    user = random.choice(USERS)
    event: Dict = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "host": random.choice(HOSTS),
        "app": random.choice(APPS),
        "action": random.choice(ACTIONS),
        "bytes": random.randint(100, 50000),
        "success": random.random() > 0.05,
    }
    # Inject anomalies more frequently to stress detection
    if random.random() < current_anomaly_rate():
        event = inject_anomaly(event)
    # Attach MITRE hints based on action
    mitre = MITRE_ACTION_MAP.get(event["action"], {"tactics": [], "techniques": []})
    if mitre["tactics"] or mitre["techniques"]:
        event["mitre_tactics"] = mitre["tactics"]
        event["mitre_techniques"] = mitre["techniques"]
    return event


def current_anomaly_rate() -> float:
    try:
        env_rate = float(os.getenv("ANOMALY_RATE", ANOMALY_RATE_DEFAULT))
    except ValueError:
        env_rate = ANOMALY_RATE_DEFAULT
    return max(0.0, min(1.0, env_rate))


def inject_anomaly(event: Dict) -> Dict:
    anomaly_type = random.choice(["exfil", "bruteforce", "rare_app"])
    if anomaly_type == "exfil":
        event["bytes"] = random.randint(300_000, 800_000)
        event["action"] = "exfiltration"
        event["success"] = True
    elif anomaly_type == "bruteforce":
        event["action"] = "login"
        event["success"] = False
        event["attempts"] = random.randint(5, 20)
    else:
        event["app"] = "admin-console"
        event["action"] = "access_denied"
        event["bytes"] = random.randint(1_000, 3_000)
    return event


def main() -> None:
    delay = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    if len(sys.argv) > 2:
        os.environ["ANOMALY_RATE"] = sys.argv[2]
    while True:
        evt = generate_event()
        sys.stdout.write(json.dumps(evt) + "\n")
        sys.stdout.flush()
        time.sleep(delay)


if __name__ == "__main__":
    main()
