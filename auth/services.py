# auth/services.py
from fastapi import UploadFile, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, join
from auth.models import Users
from core.database import sessionLocal
from core.mail import sendVerificationEmail, sendResetPasswordEmail, resendEmalLink
from utils.hashing import hashPassword, verifyPassword
from utils.token import create_access_token
from utils.token import decode_token
from datetime import datetime, timezone, timedelta
from auth.schemas import userSchema
import os, uuid


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def registerService(req: userSchema, image: UploadFile = None):
    db = sessionLocal()
    try:
        existing = db.query(Users).filter(Users.email == req.email).first()
        if existing:
            raise HTTPException(status_code=401, detail="Email already registered")

        hashed_password = hashPassword(str(req.password).strip())

        image_path = None
        if image:
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image_path = image_path.replace("\\", "/")
            with open(image_path, "wb") as f:
                f.write(await image.read())
        token = create_access_token(
                data = {"sub": req.email, "purpose": "email_verification"},
                expires_delta = timedelta(hours=24)
            )
            
        user = Users(
            name        = req.name,
            email       = req.email,
            phonenumber = req.phonenumber,
            password    = hashed_password,
            location    = req.location,
            status      = "offline",
            image       = image_path,
            is_active    = False,    # ✅ inactive until verified
            verify_token = token
        )
        db.add(user)
        db.commit()
        # send verification email
        await sendVerificationEmail(req.email, token)
        return {"response": "User registered successfully"}
    finally:
        db.close()
        
async def verifyEmailService(token: str):
    db = sessionLocal()
    try:
        # decode token
        payload = decode_token(token)
        user_id   = payload.get("sub")
        print("payload", user_id)
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token")

        # find user
        user = db.query(Users).filter(           
             or_(
                and_(
                    Users.id == user_id,
                    Users.verify_token == token
                ),
                and_(
                    Users.email == user_id,
                    Users.verify_token == token
                )
            )
        ).first()

        if not user:
            raise HTTPException(status_code=400, detail="Invalid or already used token")

        if user.is_active:
            raise HTTPException(status_code=400, detail="Account already verified")

        # activate account
        user.is_active    = True
        user.verify_token = None  # clear token after use
        db.commit()

        return {"response": "Email verified successfully! You can now login."}

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    finally:
        db.close()
        
async def resendEmailService(body: dict):
    db = sessionLocal()
    email = body.get("email")
    user = db.query(Users).filter(Users.email == email).first()

    # Always return 200 — never reveal if email exists
    if not user or user.is_active:
        return {"message": "If that email exists, a new link was sent."}

    # Generate fresh token
    token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(hours=24)
    )
    # activate account
    user.verify_token = token  # clear token after use
    db.commit()
    await resendEmalLink(email, token)

    return {"message": "Verification email sent."}

        
async def getProfileService(data: str):
    return {
        "id"          : data.id,
        "name"        : data.name,
        "email"       : data.email,
        "phonenumber" : data.phonenumber,
        "location"    : data.location,
        "image"       : data.image
    }

async def updateProfileService(name, phonenumber, location, image, tokenData):
    db = sessionLocal()
    try:
        user = db.query(Users).filter(Users.id == tokenData.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # update fields
        user.name        = name
        user.phonenumber = phonenumber
        user.location    = location

        # update image if provided
        if image:
            ext      = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            path     = os.path.join(UPLOAD_FOLDER, filename)
            path = path.replace("\\", "/")
            
            with open(path, "wb") as f:
                f.write(await image.read())
            user.image = path

        db.commit()
        return {
            "response"    : "Profile updated successfully",
            "name"        : user.name,
            "phonenumber" : user.phonenumber,
            "location"    : user.location,
            "image"       : user.image
        }
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
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Please verify your email before logging in")
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
            "email"  : user.email,
            "image"  : user.image
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
        
async def forgotPasswordService(email: str):
    db = sessionLocal()
    try:
        user = db.query(Users).filter(Users.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Email not found")

        # generate reset token — expires in 1 hour
        token = create_access_token(
            data          = {"sub": email, "purpose": "reset_password"},
            expires_delta = timedelta(hours=1)
        )

        # send reset email
        await sendResetPasswordEmail(email, token)
        return {"response": "Password reset link sent to your email"}
    finally:
        db.close()

async def resetPasswordService(token: str, new_password: str):
    db = sessionLocal()
    try:
        # decode token
        payload = decode_token(token)
        email   = payload.get("sub")
        purpose = payload.get("purpose")

        # verify it's a reset token
        if purpose != "reset_password":
            raise HTTPException(status_code=400, detail="Invalid token")

        # find user
        user = db.query(Users).filter(Users.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # validate new password
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

        # update password
        user.password = hashPassword(new_password)
        db.commit()
        return {"response": "Password reset successfully! You can now login."}

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    finally:
        db.close()
        
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