from jose import jwt
from jose import JWTError
from datetime import datetime, timedelta, timezone

SECRET_KEY = "CHANDRIKA$qazplm"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

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