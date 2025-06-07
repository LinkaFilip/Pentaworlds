from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()  # musí být dřív než os.getenv

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL = '{DATABASE_URL}'")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not set in environment variables")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
print("Everything is good from database.py")
