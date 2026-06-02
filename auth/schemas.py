# schemas is a place where sent or receive data in below mentioned formate and do validation using pydantic

from pydantic import BaseModel, EmailStr
from typing import Optional

class userSchema(BaseModel):
    name: str
    email: EmailStr
    phonenumber:str
    password:str
    location:str
         
class loginSchema(BaseModel):
    email: EmailStr
    password:str
    
class logoutSchema(BaseModel):
    id: int