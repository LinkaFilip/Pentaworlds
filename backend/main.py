print("main.py načten")

import secrets
import logging
import sys
import os
import uuid

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .auth import decode_token

from backend import schemas, utils, auth, models
from backend.database import SessionLocal, engine, get_db
from backend.routers import user
from backend.auth import authenticate_user, create_access_token

app = FastAPI()

app.include_router(user.router)
models.Base.metadata.create_all(bind=engine)
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


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = auth.decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


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
        rocks=0,
        url_hash=url_hash
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
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
            "error": str(exc)
        }
    )
@app.get("/{url_hash}", response_class=HTMLResponse)
def user_world(
    url_hash: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = auth.decode_token(token)
        username = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.url_hash == url_hash).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.username != username:
        raise HTTPException(status_code=403, detail="Access denied")

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{user.username}'s World</title>
        <style>
            body {{
                background-color: #ffffff;
                color: black;
                font-family: sans-serif;
                padding: 2em;
            }}
        </style>
    </head>
    <body>
        <h1>Welcome to {user.username}'s world!</h1>
        <p>Coins: {user.coins}</p>
        <p>Rocks: {user.rocks}</p>
    </body>
    </html>
    """)
    class CoinsData(BaseModel):
        coins: int
        rocks: int



class CoinsData(BaseModel):
    coins: int
    rocks: int

@app.post("/update_coins")
def update_coins(data: CoinsData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
@app.post("/update_rocks")
def rocks(data: CoinsData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.coins = data.coins
    db.commit()
    return {"message": "Rocks updated", "rocks": user.rocks}

@app.get("/test-auth")
def test_auth(token: str = Depends(oauth2_scheme)):
    print("Token received in /test-auth:", token)
    return {"token": token}
    print("DB session:", db)
    user = db.query(User).filter(User.username == username).first()
    print("Queried user:", user)

@app.get("/protected")
def protected(user: models.User = Depends(get_current_user)):
    return {"message": f"Hello, {user.username}!"}

print("Everything is good from main.py")