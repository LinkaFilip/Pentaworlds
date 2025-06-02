from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://penta_worlds_database_user:tlrQsqkboG4qHcixoBAIAOQlzYtLpMfx@dpg-d0v0gammcj7s73cqrnm0-a/penta_worlds_database"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()