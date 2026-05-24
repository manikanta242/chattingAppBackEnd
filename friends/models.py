from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base

class FriendRequest(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_user = Column(Integer, ForeignKey("users.id"))
    to_user = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="pending")
