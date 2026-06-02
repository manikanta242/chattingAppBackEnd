from jose import jwt
from jose import JWTError
from datetime import datetime, timedelta, timezone
from core.config import (
    SECRET_KEY,
    ALGORITHM
)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ============================================================
#  DECODE TOKEN — returns payload dict
# ============================================================
def decode_token(token: str) -> dict | None:
    try:
        # ── Remove "Bearer " prefix if present ────────────────
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        # ── Decode ────────────────────────────────────────────
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"📦 Decoded payload: {payload}")
        return payload

    except JWTError as e:
        print(f"❌ Token decode error: {e}")
        return None


# ============================================================
#  VERIFY TOKEN — returns True/False
# ============================================================
def verify_token(token: str) -> bool:
    return decode_token(token) is not None