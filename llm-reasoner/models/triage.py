from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MitreAttack(BaseModel):
    tactics: List[str] = Field(default_factory=list)
    techniques: List[str] = Field(default_factory=list)


class TriageRequest(BaseModel):
    event: Dict[str, Any]
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    model: Optional[str] = Field(
        None, description="Optional model identifier for context in triage."
    )


class TriageResponse(BaseModel):
    category: str
    severity: SeverityLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    mitre_attack: MitreAttack
    mitre_rationale: List[str] = Field(default_factory=list)
    summary: str
    indicators: Dict[str, Any] = Field(default_factory=dict)
    recommended_actions: List[str] = Field(default_factory=list)
