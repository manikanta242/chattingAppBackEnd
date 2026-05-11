from auth.models import Users
from core.database import sessionLocal
from utils.hashing import hashPassword, verifyPassword
from utils.token import create_access_token

def registerService(req):
    print("--------------------------service---------------------------------------------")
    db = sessionLocal()
    password = str(req.password).strip()
    hashed_password = hashPassword(password)
    print("-----------------------------------------------------------------------")
    user = Users(
        name = req.name,
        email = req.email,
        phonenumber = req.phonenumber,
        password = hashed_password,
        location = req.location  
    )
    db.add(user)
    db.commit()
    return {
        "message": "user registered"
    }
    
def userService():
    db = sessionLocal()
    return db.query(Users).all()
    
def loginService(req):
    db = sessionLocal()
    req = Users(
        email = req.email,
        password = req.password
    )
    user = db.query(Users).filter(
        Users.email == req.email
    ).first()

    if not user:
        return None

    valid_password = verifyPassword(
        req.password,
        user.password
    )

    if not valid_password:
        return None

    token = create_access_token(
        {"sub": user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
    
    
    
    