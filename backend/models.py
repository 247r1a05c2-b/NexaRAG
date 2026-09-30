from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field

SourceType = Literal["log", "alert", "ticket", "deployment", "chat", "metric"]

class EventIn(BaseModel):
    source_type: SourceType
    service: str = "unknown"
    timestamp: datetime | None = None
    message: str = ""
    severity: str = "info"
    metadata: dict[str, Any] = Field(default_factory=dict)

class IncidentCreate(BaseModel):
    title: str
    description: str = ""

class Proposal(BaseModel):
    action: str
    rationale: str
    risk: Literal["low", "medium", "high"]
    safe_to_execute: bool = False
    requires_human: bool = True
    verification: str
    status: Literal["pending", "approved", "rejected"] = "pending"

class Incident(BaseModel):
    id: str
    title: str
    description: str
    status: str = "open"
    created_at: datetime
    events: list[EventIn] = Field(default_factory=list)
    hypotheses: list[dict[str, Any]] = Field(default_factory=list)
    timeline: list[dict[str, Any]] = Field(default_factory=list)
    proposals: list[Proposal] = Field(default_factory=list)
    summary: str = ""
    analysis_version: str = "1.0"


def now() -> datetime:
    return datetime.now(timezone.utc)
