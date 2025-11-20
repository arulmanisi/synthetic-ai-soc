from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    """Input schema for scoring."""

    event: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary event payload to score."
    )


class ScoreResponse(BaseModel):
    """Score output schema."""

    score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score.")
    model: str = Field(..., description="Model that produced the score.")


class ModelListResponse(BaseModel):
    """Available models metadata."""

    models: List[str] = Field(default_factory=list, description="Model names.")
