from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from models.triage import TriageRequest, TriageResponse, SeverityLevel, MitreAttack
from prompts.triage_prompt import build_triage_prompt, get_mitre_hints

app = FastAPI(title="LLM Reasoner")

class ExplainRequest(BaseModel):
    alert_id: int
    alert_data: Dict[str, Any]

class ExplainResponse(BaseModel):
    explanation: str
    recommended_actions: list[str]

@app.post("/explain", response_model=ExplainResponse)
def explain_alert(request: ExplainRequest):
    # Placeholder for actual LLM call (e.g., OpenAI, Anthropic, or local LLM)
    # For MVP, we return a static or template-based explanation.
    
    alert = request.alert_data
    severity = alert.get("severity", "unknown")
    source = alert.get("source", "unknown")
    
    explanation = (
        f"This alert indicates a potential security incident with {severity} severity "
        f"detected by {source}. The system observed anomalous behavior that deviates "
        f"from the established baseline."
    )
    
    actions = [
        "Investigate the source IP address.",
        "Check user activity logs for the affected account.",
        "Verify if this is a known false positive."
    ]
    
    return ExplainResponse(
        explanation=explanation,
        recommended_actions=actions
    )


@app.post("/triage", response_model=TriageResponse)
def triage_alert(request: TriageRequest):
    """
    Perform intelligent triage on a security alert.
    
    This endpoint uses LLM reasoning to categorize, assess severity,
    map to MITRE ATT&CK, and provide actionable recommendations.
    
    For MVP, this uses rule-based logic. In production, replace with actual LLM calls.
    """
    
    # Build the prompt (useful for real LLM integration)
    prompt = build_triage_prompt(request.event, request.anomaly_score, request.model)
    
    # Mock LLM response using rule-based logic
    # In production, replace this with: llm_client.generate(prompt)
    triage = _mock_llm_triage(request.event, request.anomaly_score)
    
    return triage


def _mock_llm_triage(event: Dict[str, Any], anomaly_score: float) -> TriageResponse:
    """
    Mock LLM triage using rule-based logic.
    Replace this with actual LLM API calls in production.
    """
    
    action = event.get("action", "").lower()
    user = event.get("user", "unknown")
    source_ip = event.get("source_ip", event.get("src_ip", "unknown"))
    
    # Determine category based on action
    if "login" in action or "auth" in action:
        category = "Credential Access"
        summary = f"Anomalous authentication activity detected for user '{user}' from IP {source_ip}."
        actions = [
            f"Verify legitimacy of login attempt from {source_ip}",
            f"Check if user '{user}' recognizes this activity",
            "Review authentication logs for the past 24 hours",
            "Consider implementing MFA if not already enabled"
        ]
    elif "file" in action or "read" in action or "write" in action:
        category = "Data Exfiltration"
        summary = f"Unusual file access pattern detected for user '{user}'."
        actions = [
            "Identify which files were accessed",
            "Determine if data left the network",
            "Review DLP policies and alerts",
            "Interview the user about their file access"
        ]
    elif "process" in action or "exec" in action:
        category = "Execution"
        summary = f"Suspicious process execution detected on system associated with '{user}'."
        actions = [
            "Isolate the affected system",
            "Capture process memory dump",
            "Run malware scan",
            "Review process execution logs"
        ]
    elif "network" in action or "connect" in action:
        category = "Command and Control"
        summary = f"Unusual network connection detected from user '{user}'."
        actions = [
            "Block suspicious destination IP/domain",
            "Capture network traffic for analysis",
            "Check threat intelligence feeds",
            "Investigate the application making the connection"
        ]
    else:
        category = "Discovery"
        summary = f"Anomalous behavior detected for user '{user}' - requires investigation."
        actions = [
            "Review full event context",
            "Check for related alerts",
            "Investigate user's recent activity",
            "Consult with security team"
        ]
    
    # Determine severity based on anomaly score
    if anomaly_score >= 0.9:
        severity = SeverityLevel.CRITICAL
    elif anomaly_score >= 0.7:
        severity = SeverityLevel.HIGH
    elif anomaly_score >= 0.5:
        severity = SeverityLevel.MEDIUM
    else:
        severity = SeverityLevel.LOW
    
    # Get MITRE ATT&CK hints
    mitre_hints = get_mitre_hints(event)
    mitre_attack = MitreAttack(
        tactics=mitre_hints.get("tactics", []),
        techniques=mitre_hints.get("techniques", [])
    )
    
    # Extract indicators
    indicators = {
        "user": user,
        "source_ip": source_ip,
        "action": action,
        "anomaly_score": anomaly_score
    }
    
    # Add any numeric fields as potential indicators
    for key, value in event.items():
        if isinstance(value, (int, float)) and key not in indicators:
            indicators[key] = value
    
    return TriageResponse(
        category=category,
        severity=severity,
        confidence=min(anomaly_score + 0.1, 1.0),  # Slightly boost confidence
        mitre_attack=mitre_attack,
        summary=summary,
        indicators=indicators,
        recommended_actions=actions
    )


@app.get("/health")
def health():
    return {"status": "ok"}
