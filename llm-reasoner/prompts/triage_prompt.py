from typing import Any, Dict, List


def build_triage_prompt(event: Dict[str, Any], anomaly_score: float, model: str | None) -> str:
    """Construct a triage prompt that can be sent to an LLM."""
    lines: List[str] = [
        "You are a SOC analyst LLM. Perform triage on the following event.",
        f"Model: {model or 'unknown'}",
        f"Anomaly score: {anomaly_score:.3f}",
        "Event:",
        str(event),
        "Decide category, severity, MITRE ATT&CK mapping, and recommended actions.",
    ]
    return "\n".join(lines)


def get_mitre_hints(event: Dict[str, Any]) -> Dict[str, List[str]]:
    """Heuristic mapping to seed MITRE ATT&CK hints."""
    action = str(event.get("action", "")).lower()
    hints: Dict[str, List[str]] = {"tactics": [], "techniques": []}

    if "login" in action or "auth" in action:
        hints["tactics"].append("Credential Access")
        hints["techniques"].append("T1110 Brute Force")
    if "file" in action or "exfil" in action:
        hints["tactics"].append("Exfiltration")
        hints["techniques"].append("T1048 Exfiltration Over Alternative Protocol")
    if "process" in action or "exec" in action:
        hints["tactics"].append("Execution")
        hints["techniques"].append("T1204 User Execution")
    if "network" in action or "connect" in action:
        hints["tactics"].append("Command and Control")
        hints["techniques"].append("T1071 Application Layer Protocol")

    return hints
