from datetime import datetime
from typing import Optional, List, Dict, Any
import json

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field

Base = declarative_base()

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String, index=True) # e.g., "anomaly-service"
    
    # Triage fields
    category = Column(String, default="Uncategorized")
    severity = Column(String) # low, medium, high, critical
    confidence = Column(Float, default=0.0)
    
    description = Column(Text) # Summary
    raw_event = Column(Text) # JSON string of the original event
    
    # ML fields
    score = Column(Float)
    model = Column(String)
    
    # Context
    mitre_tactics = Column(JSON, default=list)
    mitre_techniques = Column(JSON, default=list)
    indicators = Column(JSON, default=dict)
    recommended_actions = Column(JSON, default=list)
    
    is_resolved = Column(Boolean, default=False)
    
class AlertCreate(BaseModel):
    source: str = "synthetic-ai-soc"
    category: str = "Uncategorized"
    severity: str = "low"
    confidence: float = 0.0
    description: str
    raw_event: str
    score: float
    model: str = "unknown"
    mitre_tactics: List[str] = []
    mitre_techniques: List[str] = []
    indicators: Dict[str, Any] = {}
    recommended_actions: List[str] = []

class AlertRead(AlertCreate):
    id: int
    timestamp: datetime
    is_resolved: bool

    class Config:
        orm_mode = True
