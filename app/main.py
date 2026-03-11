from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models, schemas, crud, utils, auth
from .dependencies import get_current_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ---------- SIGNUP ----------

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = crud.get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = utils.hash_password(user.password)

    crud.create_user(db, user, hashed_password)

    return {"message": "User created successfully"}


# ---------- LOGIN ----------

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


# ---------- CREATE TASK ----------

@app.post("/tasks")
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    return crud.create_task(db, task, current_user.id)


# ---------- GET TASKS ----------

@app.get("/tasks")
def get_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    return crud.get_tasks(db, current_user.id)


# ---------- UPDATE TASK ----------

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


# ---------- DELETE TASK ----------

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