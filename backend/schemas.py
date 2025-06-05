from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    coins: int
    hash_url: str

    class Config:
        from_attributes = True  # nebo orm_mode = True pokud používáš Pydantic v1

class Token(BaseModel):
    access_token: str
    token_type: str

print("Everything is good from schemas.py");
