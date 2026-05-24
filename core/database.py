from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import (
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DATABASE
)

# ✅ Build DB URL from config
DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

DATABASE_URL2 = "mysql+pymysql://root:root@localhost/chatapplication"

print("database url", DATABASE_URL, DATABASE_URL2)

Base = declarative_base()
engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def create_db():
    import auth.models
    import message.models
    import friends.models

    Base.metadata.create_all(bind=engine)