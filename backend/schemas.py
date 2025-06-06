from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    coins: int
    rocks: int
    url_hash: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

print("Everything is good from schemas.py");
