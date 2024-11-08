# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('RENDER_DATABASE_USER')}:{os.getenv('RENDER_DATABASE_PASSWORD')}@{os.getenv('RENDER_DATABASE_HOST')}:{os.getenv('RENDER_DATABASE_PORT')}/{os.getenv('RENDER_DATABASE_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()