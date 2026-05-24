from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy import Column, DateTime, func
from core.database import Base
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    context = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())