from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EventContext(BaseModel):
    source: Optional[str] = Field(
        None, description="Logical source identifier (e.g., auth, network, endpoint)."
    )
    tenant_id: Optional[str] = Field(
        None, description="Tenant or environment identifier for multi-tenancy."
    )
    tags: List[str] = Field(default_factory=list, description="Optional labels.")


class AnomalyEvent(BaseModel):
    """Schema for incoming events to score."""

    event_id: str = Field(..., description="Unique identifier for this event.")
    timestamp: datetime = Field(..., description="Event timestamp.")
    entity: Optional[str] = Field(
        None, description="Primary entity or principal involved in the event."
    )
    features: Dict[str, float] = Field(
        default_factory=dict,
        description="Engineered feature vector used for anomaly scoring.",
    )
    raw: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw event payload for enrichment/debug traceability.",
    )
    context: Optional[EventContext] = Field(
        None, description="Additional routing or tenancy context."
    )


class ScoreResponse(BaseModel):
    event_id: str
    anomaly_score: float
    model_version: str
    threshold: float
    is_anomaly: bool
    reason: Optional[str] = None


class BatchScoreRequest(BaseModel):
    events: List[AnomalyEvent] = Field(
        default_factory=list, description="Events to score in a single request."
    )


class BatchScoreResponse(BaseModel):
    results: List[ScoreResponse] = Field(
        default_factory=list, description="Ordered results matching the request list."
    )
