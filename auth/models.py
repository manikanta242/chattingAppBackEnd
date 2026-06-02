from sqlalchemy import Column, Integer, String, Boolean
from core.database import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    email= Column(String(255), index=True)
    phonenumber=Column(String(255), index=True)
    password= Column(String(255))
    location= Column(String(255)) 
    status = Column(String(50), default="offline")
    image = Column(String(500), nullable=True)
    is_active   = Column(Boolean, default=False) 
    verify_token = Column(String(500), nullable=True) 