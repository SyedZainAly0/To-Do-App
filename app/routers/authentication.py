from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, crud, utils, auth

app = FastAPI()


# ---------------- SIGNUP ----------------

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = crud.get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = utils.hash_password(user.password)

    new_user = crud.create_user(db, user, hashed_password)

    return {"message": "User created successfully"}


# ---------------- LOGIN ----------------

@app.post("/login", response_model=schemas.LoginResponse)
def login(user: schemas.LoginRequest, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(db, user.email)

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not utils.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = auth.create_access_token(data={"user_id": db_user.id})

    return {
        "message": "Login Successfully",
        "access_token": token
    }