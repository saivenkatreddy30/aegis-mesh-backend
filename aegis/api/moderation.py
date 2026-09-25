from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from aegis.core.config import settings
from aegis.core.database import get_db
from aegis.security.auth import verify_password, create_jwt_token
from aegis.models.escrow import EscrowReport, IncidentStatus, IncidentCategory
from aegis.models.moderator import ModeratorOfficer
from aegis.schemas.escrow import EscrowModeratorDetailResponse, StatusTransitionRequest
from aegis.schemas.moderator import TokenEnvelope, ModeratorLoginRequest

router = APIRouter(prefix="/moderator", tags=["Moderation Console (RBAC Restricted)"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/moderator/auth/token")

VALID_TRANSITIONS = {
    IncidentStatus.SUBMITTED: {IncidentStatus.UNDER_REVIEW},
    IncidentStatus.UNDER_REVIEW: {IncidentStatus.RESOLVED, IncidentStatus.DISMISSED},
    IncidentStatus.RESOLVED: set(),
    IncidentStatus.DISMISSED: set(),
}

def get_current_moderator(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> ModeratorOfficer:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired moderator session token.",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise exc
    except JWTError:
        raise exc

    officer = db.query(ModeratorOfficer).filter(ModeratorOfficer.username == username).first()
    if not officer:
        raise exc
    return officer

@router.post("/auth/token", response_model=TokenEnvelope)
def authenticate_moderator(creds: ModeratorLoginRequest, db: Session = Depends(get_db)):
    officer = db.query(ModeratorOfficer).filter(ModeratorOfficer.username == creds.username).first()
    if not officer or not verify_password(creds.password, officer.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid officer credentials")
    
    token = create_jwt_token(data={"sub": officer.username, "title": officer.badge_title})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/feed", response_model=List[EscrowModeratorDetailResponse])
def get_prioritized_reports(
    category: Optional[IncidentCategory] = None,
    status_filter: Optional[IncidentStatus] = None,
    db: Session = Depends(get_db),
    _: ModeratorOfficer = Depends(get_current_moderator)
):
    query = db.query(EscrowReport)
    if category:
        query = query.filter(EscrowReport.category == category)
    if status_filter:
        query = query.filter(EscrowReport.status == status_filter)
    return query.order_by(EscrowReport.urgency_score.desc()).all()

@router.patch("/reports/{token}/transition", response_model=EscrowModeratorDetailResponse)
def execute_status_transition(
    token: str,
    body: StatusTransitionRequest,
    db: Session = Depends(get_db),
    _: ModeratorOfficer = Depends(get_current_moderator)
):
    report = db.query(EscrowReport).filter(EscrowReport.claim_token == token.strip().upper()).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report record not found")

    allowed_next_states = VALID_TRANSITIONS.get(report.status, set())
    if body.new_status not in allowed_next_states:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Illegal state transition from {report.status} to {body.new_status}. Allowed next states: {[s.value for s in allowed_next_states]}"
        )

    report.status = body.new_status
    if body.resolution_note:
        report.moderator_resolution_note = body.resolution_note

    db.commit()
    db.refresh(report)
    return report