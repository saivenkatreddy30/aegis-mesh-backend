from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from aegis.core.database import Base

class ModeratorOfficer(Base):
    __tablename__ = "moderator_officers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    badge_title = Column(String(64), default="Investigative Moderator")
    created_at = Column(DateTime, default=datetime.utcnow)