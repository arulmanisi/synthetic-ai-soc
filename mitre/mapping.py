from typing import Dict, List

# Simple heuristic mapping of actions/fields to MITRE ATT&CK tactics/techniques
MITRE_ACTION_MAP: Dict[str, Dict[str, List[str]]] = {
    "login_failed": {
        "tactics": ["Credential Access"],
        "techniques": ["T1110 Brute Force"],
    },
    "login": {
        "tactics": ["Initial Access", "Credential Access"],
        "techniques": ["T1078 Valid Accounts"],
    },
    "file_read": {
        "tactics": ["Exfiltration"],
        "techniques": ["T1048 Exfiltration Over Alternative Protocol"],
    },
    "file_access": {
        "tactics": ["Exfiltration"],
        "techniques": ["T1048 Exfiltration Over Alternative Protocol"],
    },
    "exfiltration": {
        "tactics": ["Exfiltration"],
        "techniques": ["T1041 Exfiltration Over Command and Control Channel"],
    },
    "process_exec": {
        "tactics": ["Execution"],
        "techniques": ["T1059 Command and Scripting Interpreter"],
    },
    "network_connect": {
        "tactics": ["Command and Control"],
        "techniques": ["T1071 Application Layer Protocol"],
    },
    "lateral_movement": {
        "tactics": ["Lateral Movement"],
        "techniques": ["T1021 Remote Services"],
    },
    "discovery_scan": {
        "tactics": ["Discovery"],
        "techniques": ["T1046 Network Service Scanning", "T1083 File and Directory Discovery"],
    },
    "access_denied": {
        "tactics": ["Discovery"],
        "techniques": ["T1083 File and Directory Discovery"],
    },
}


def mitre_hints_for_action(action: str) -> Dict[str, List[str]]:
    key = action.lower()
    return MITRE_ACTION_MAP.get(key, {"tactics": [], "techniques": []})
