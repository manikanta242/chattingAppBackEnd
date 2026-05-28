# core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from core.config import DATABASE_URL

engine       = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base         = declarative_base()

def create_db():
    Base.metadata.create_all(bind=engine)