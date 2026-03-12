from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from .database import engine, get_db
from . import models, schemas, crud, utils, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ------------------ GET CURRENT USER ------------------

def get_current_user(access_token: str = Cookie(None), db: Session = Depends(get_db)):

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(access_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ------------------ SIGNUP ------------------

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = utils.hash_password(user.password)
    crud.create_user(db, user, hashed_password)
    return {"message": "User created successfully"}


# ------------------ LOGIN ------------------

@app.post("/login")
def login(user: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(db, user.email)
    if not db_user or not utils.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = auth.create_access_token(data={"user_id": db_user.id})

    # Set JWT in HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"  # optional, prevents CSRF in some cases
    )

    return {"message": "Login successful"}


# ------------------ TASK ROUTES ------------------

@app.post("/tasks")
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_task(db, task, current_user.id)


@app.get("/tasks")
def get_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_tasks(db, current_user.id)


@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_task = crud.get_task(db, task_id)
    if not db_task or db_task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.update_task(db, task_id, task)


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_task = crud.get_task(db, task_id)
    if not db_task or db_task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.delete_task(db, task_id)
    return {"message": "Task deleted successfully"}