from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    email= Column(String(255), index=True)
    phonenumber=Column(String(255), index=True)
    password= Column(String(255))
    location= Column(String(255)) 