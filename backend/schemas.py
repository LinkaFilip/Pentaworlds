from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    coins: int
    hash_url: str

    model_config = {
        "from_attributes": True  # Pro Pydantic v2 (dříve orm_mode=True)
    }
class Token(BaseModel):
    access_token: str
    token_type: str
print("Everything is good from schemas.py");
