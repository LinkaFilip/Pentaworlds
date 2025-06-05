import secrets
import logging
import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from fastapi import FastAPI, Depends, HTTPException, status
from models import User
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import authenticate_user, create_access_token
# Všechny importy jako moduly z backendu:
from database import SessionLocal, engine
import models
import schemas
import utils
import schemas
import auth
from schemas import Token
# Vytvoření tabulek
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pentaworlds.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
@app.get("/")
def read_root():
    return {"Hello": "World"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(f"Received signup request: {user.username}")
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = utils.hash_password(user.password)
    url_hash = secrets.token_hex(6)  # 12 znaků

    new_user = models.User(
        username=user.username,
        hashed_password=hashed_pw,
        coins=0,
        url_hash=url_hash
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)  # <-- přidej toto
):
    user = authenticate_user(db, form_data.username, form_data.password)  # <-- a tady předej `db`
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserOut)
def get_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = auth.decode_token(token)
        username = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.exception("Unhandled error occurred")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)  # <-- přidej přesný text chyby
        }
    )
@app.get("/{url_hash}", response_class=HTMLResponse)
def user_world(url_hash: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.url_hash == url_hash).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{user.username}'s World</title>
        <style>
            body {{
                background-color: #111;
                color: #eee;
                font-family: sans-serif;
                padding: 2em;
            }}
        </style>
    </head>
    <body>
        <h1>Welcome to {user.username}'s world!</h1>
        <p>Coins: {user.coins}</p>
    </body>
    </html>
    """)
    class CoinsData(BaseModel):
        coins: int

@app.post("/update_coins")
def update_coins(data: CoinsData, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.coins = data.coins
    db.commit()
    return {"message": "Coins updated", "coins": user.coins}
print("Everything is good from main.py")