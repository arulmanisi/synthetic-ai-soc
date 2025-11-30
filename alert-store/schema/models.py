from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String, index=True) # e.g., "anomaly-service"
    severity = Column(String) # low, medium, high, critical
    description = Column(Text)
    raw_event = Column(Text) # JSON string of the original event
    score = Column(Float)
    is_resolved = Column(Boolean, default=False)
    
class AlertCreate(BaseModel):
    source: str
    severity: str
    description: str
    raw_event: str
    score: float

class AlertRead(AlertCreate):
    id: int
    timestamp: datetime
    is_resolved: bool

    class Config:
        orm_mode = True
