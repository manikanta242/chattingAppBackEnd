# auth.py
from fastapi            import Depends, HTTPException
from fastapi.security   import OAuth2PasswordBearer
from jose               import JWTError, jwt
from core.database           import sessionLocal
from auth.models             import Users

SECRET_KEY = "CHANDRIKA$qazplm"
ALGORITHM  = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email:   str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if not email or not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        db   = sessionLocal()
        user = db.query(Users).filter(Users.id == user_id).first()
        db.close()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")