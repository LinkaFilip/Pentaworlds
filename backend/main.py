import secrets
import logging
import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Depends, HTTPException, status
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
    hash_url = secrets.token_hex(6)  # 12 znaků

    new_user = models.User(
        username=user.username,
        hashed_password=hashed_pw,
        coins=0,
        hash_url=hash_url
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
        content={"detail": "Internal server error"}
    )
print("Everything is good from main.py")