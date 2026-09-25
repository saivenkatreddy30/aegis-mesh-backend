from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from aegis.models.escrow import IncidentCategory, IncidentStatus, UrgencyLevel

class EscrowCreate(BaseModel):
    category: IncidentCategory
    description: str = Field(..., min_length=10, description="Factual narrative of the incident")
    evidence_url: Optional[str] = Field(None, description="Optional evidence link")

class EscrowPublicResponse(BaseModel):
    claim_token: str
    status: IncidentStatus
    category: IncidentCategory
    moderator_resolution_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EscrowModeratorDetailResponse(EscrowPublicResponse):
    id: int
    sanitized_narrative: str
    redaction_count: int
    urgency_level: UrgencyLevel
    urgency_score: float
    evidence_reference: Optional[str] = None

class StatusTransitionRequest(BaseModel):
    new_status: IncidentStatus
    resolution_note: Optional[str] = Field(None, max_length=1000)