import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, Float
from aegis.core.database import Base

class IncidentCategory(str, enum.Enum):
    SECURITY = "Security"
    HARASSMENT = "Harassment"
    CORRUPTION = "Corruption"
    TECHNICAL = "Technical"
    OTHER = "Other"

class IncidentStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

class UrgencyLevel(str, enum.Enum):
    CRITICAL = "Critical"
    ELEVATED = "Elevated"
    STANDARD = "Standard"

class EscrowReport(Base):
    __tablename__ = "escrow_reports"

    id = Column(Integer, primary_key=True, index=True)
    claim_token = Column(String(32), unique=True, index=True, nullable=False)
    category = Column(Enum(IncidentCategory), nullable=False)
    sanitized_narrative = Column(Text, nullable=False)
    redaction_count = Column(Integer, default=0)
    urgency_level = Column(Enum(UrgencyLevel), default=UrgencyLevel.STANDARD)
    urgency_score = Column(Float, default=0.0)
    evidence_reference = Column(String(512), nullable=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.SUBMITTED, nullable=False)
    moderator_resolution_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)