# core/config.py
import os
from dotenv import load_dotenv

# ✅ Load .env file
load_dotenv()

# ✅ Get DATABASE_URL directly — no MYSQL_USER etc.
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("MYSQLDATABASE_URL", "")

# ✅ Fix prefix for SQLAlchemy
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    
# ✅ Fallback for local development
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/chatapplication"

# ── JWT ───────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "CHANDRIKA$qazplm")
ALGORITHM  = os.getenv("ALGORITHM","HS256")
APP_PORT   = int(os.getenv("APP_PORT", "8000"))
DEBUG      = os.getenv("DEBUG", "True") == "True"

# ── EMAIL ───────────────────────────────────────────
FRONTEND_URL  = os.getenv("FRONTEND_URL", "http://localhost:4200")
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "chatapplication.notify@gmail.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD","aczcfjbujnhacrtg")
MAIL_FROM     = os.getenv("MAIL_FROM","chatapplication.notify@gmail.com")
MAIL_PORT     = int(os.getenv("MAIL_PORT", 587))
MAIL_SERVER   = os.getenv("MAIL_SERVER","smtp.gmail.com")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print(f"✅ Config loaded")