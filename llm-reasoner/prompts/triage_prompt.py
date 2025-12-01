from typing import Any, Dict, List

from mitre.mapping import mitre_hints_for_action


def build_triage_prompt(event: Dict[str, Any], anomaly_score: float, model: str | None) -> str:
    """Construct a triage prompt that can be sent to an LLM."""
    mitre_hints = get_mitre_hints(event)
    lines: List[str] = [
        "You are a SOC analyst LLM. Perform triage on the following event.",
        f"Model: {model or 'unknown'}",
        f"Anomaly score: {anomaly_score:.3f}",
        f"MITRE hints: tactics={mitre_hints.get('tactics', [])}, techniques={mitre_hints.get('techniques', [])}",
        "Event:",
        str(event),
        "Decide category, severity, MITRE ATT&CK mapping, and recommended actions.",
    ]
    return "\n".join(lines)


def get_mitre_hints(event: Dict[str, Any]) -> Dict[str, List[str]]:
    """Heuristic mapping to seed MITRE ATT&CK hints."""
    action = str(event.get("action", "")).lower()
    hints = mitre_hints_for_action(action)
    return {"tactics": hints.get("tactics", []), "techniques": hints.get("techniques", [])}
