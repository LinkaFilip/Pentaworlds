from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class UpdateCoinsRequest(BaseModel):
    coins: int
    rocks: int

@router.post("/update_coins")
def update_coins(data: UpdateCoinsRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.coins = data.coins
    db.commit()
    db.refresh(user)
    return {"message": "Coins updated", "coins": user.coins}
    
@router.post("/update_rocks")
def update_rocks(data: UpdateCoinsRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.rocks = data.rocks
    db.commit()
    db.refresh(user)
    return {"message": "Rocks updated", "rocks": user.rocks}
