# core/config.py
import os
from dotenv import load_dotenv

# ✅ Load .env file
load_dotenv()

# # ── Database ──────────────────────────────────────────────────
# MYSQL_HOST     = os.getenv("MYSQL_HOST",     "mysql.railway.internal")
# MYSQL_PORT     = os.getenv("MYSQL_PORT",     "3306")
# MYSQL_USER     = os.getenv("MYSQL_USER",     "root")
# MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "ZmXfldobQnbVPPbMNdBVSNJjoUhXMeAv")
# MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "chatapplication")

# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ Single DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ✅ Fix prefix
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# ── JWT ───────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "CHANDRIKA$qazplm")
ALGORITHM  = "HS256"
APP_PORT   = int(os.getenv("APP_PORT", "8000"))
DEBUG      = os.getenv("DEBUG", "True") == "True"

print(f"✅ Config loaded")