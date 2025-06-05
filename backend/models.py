import secrets
from sqlalchemy import Column, Integer, String
from database import Base

def generate_url_hash():
    return secrets.token_hex(12)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    coins = Column(Integer, default=0)
    url_hash = Column(String, unique=True, index=True, default=generate_url_hash)

print("Everything is good from models.py")
