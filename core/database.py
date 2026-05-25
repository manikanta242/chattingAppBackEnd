# core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# ✅ Get DATABASE_URL directly — no MYSQL_USER etc.
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ✅ Fix prefix for SQLAlchemy
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

print(f"✅ DATABASE_URL exists: {bool(DATABASE_URL)}")

engine       = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base         = declarative_base()

def create_db():
    Base.metadata.create_all(bind=engine)