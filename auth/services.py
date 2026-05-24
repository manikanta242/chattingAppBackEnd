# auth/services.py
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from auth.models import Users
from core.database import sessionLocal
from utils.hashing import hashPassword, verifyPassword
from utils.token import create_access_token
from auth.schemas import userSchema

def registerService(req: userSchema):
    db = sessionLocal()
    try:
        # Check if email already registered
        existing = db.query(Users).filter(Users.email == req.email).first()
        if existing:
            raise HTTPException(status_code=401, detail="Email already registered")

        hashed_password = hashPassword(str(req.password).strip())
        user = Users(
            name        = req.name,
            email       = req.email,
            phonenumber = req.phonenumber,
            password    = hashed_password,
            location    = req.location,
            status      = "offline"
        )
        db.add(user)
        db.commit()
        return {"response": "User registered successfully"}
    finally:
        db.close()


def userService():
    db = sessionLocal()
    try:
        return db.query(Users).all()
    finally:
        db.close()


def loginService(req):
    db = sessionLocal()
    try:
        user = db.query(Users).filter(Users.email == req.email).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email")

        valid_password = verifyPassword(req.password, user.password)
        if not valid_password:
            raise HTTPException(status_code=401, detail="Invalid password")

        user.status = "online"
        db.commit()
        db.refresh(user)
        token = create_access_token({
            "sub"    : user.email,
            "user_id": user.id
        })

        return {
            "token"  : "Bearer " + token,
            "user_id": user.id,
            "name"   : user.name,
            "email"  : user.email
        }

    except HTTPException:
        raise  # re-raise HTTP exceptions as-is

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        db.close()  # always runs, even if an exception is raised
        

def logoutService(req):
    db = sessionLocal()
    try:
        user = db.query(Users).filter(Users.id == req.id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Update status to offline
        user.status = "offline"
        db.commit()

        return {"message": "Logged out successfully"}

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        db.close()