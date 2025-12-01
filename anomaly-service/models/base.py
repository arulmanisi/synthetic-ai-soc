from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    """Input schema for scoring."""

    event: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary event payload to score."
    )
    model: str | None = Field(
        None, description="Optional model override; defaults to service config."
    )
    threshold: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Optional threshold override; defaults to service config.",
    )


class ScoreResponse(BaseModel):
    """Score output schema."""

    score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score.")
    model: str = Field(..., description="Model that produced the score.")
    threshold: float = Field(..., ge=0.0, le=1.0, description="Decision threshold.")
    is_anomaly: bool = Field(..., description="True when score >= threshold.")
    mitre_tactics: List[str] = Field(default_factory=list, description="MITRE tactics hints.")
    mitre_techniques: List[str] = Field(
        default_factory=list, description="MITRE techniques hints."
    )


class ModelListResponse(BaseModel):
    """Available models metadata."""

    models: List[str] = Field(default_factory=list, description="Model names.")
