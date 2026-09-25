from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from aegis.core.database import get_db
from aegis.security.crypto import generate_claim_token
from aegis.models.escrow import EscrowReport, IncidentStatus
from aegis.schemas.escrow import EscrowCreate, EscrowPublicResponse
from aegis.services.sanitizer import execute_privacy_redaction
from aegis.services.triage import evaluate_threat_matrix

router = APIRouter(prefix="/escrow", tags=["Public Threat Escrow (Zero-Knowledge)"])

@router.post("/submit", response_model=EscrowPublicResponse, status_code=status.HTTP_201_CREATED)
def submit_threat_report(payload: EscrowCreate, db: Session = Depends(get_db)):
    sanitized_text, redactions = execute_privacy_redaction(payload.description)
    urgency_lvl, urgency_val = evaluate_threat_matrix(sanitized_text)
    claim_token = generate_claim_token()

    report = EscrowReport(
        claim_token=claim_token,
        category=payload.category,
        sanitized_narrative=sanitized_text,
        redaction_count=redactions,
        urgency_level=urgency_lvl,
        urgency_score=urgency_val,
        evidence_reference=payload.evidence_url,
        status=IncidentStatus.SUBMITTED
    )

    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("/track/{token}", response_model=EscrowPublicResponse)
def query_escrow_status(token: str, db: Session = Depends(get_db)):
    report = db.query(EscrowReport).filter(EscrowReport.claim_token == token.strip().upper()).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified claim token was not found or is invalid."
        )
    return report