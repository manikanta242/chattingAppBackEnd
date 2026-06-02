from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timedelta
from core.database import Base

class Status(Base):
    __tablename__ = "statuses"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    content    = Column(String(500), nullable=True)   # text status
    image      = Column(String(500), nullable=True)   # image status
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))