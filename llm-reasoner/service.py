from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

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

@app.get("/health")
def health():
    return {"status": "ok"}
