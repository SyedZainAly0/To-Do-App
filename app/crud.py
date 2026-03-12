from sqlalchemy.orm import Session
from . import models, schemas





def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# ---------- USER CRUD ----------

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):

    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_active=True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_email(db: Session, email: str):

    return db.query(models.User).filter(models.User.email == email).first()


def get_user(db: Session, user_id: int):

    return db.query(models.User).filter(models.User.id == user_id).first()


# ---------- TASK CRUD ----------

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):

    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        owner_id=user_id
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


def get_tasks(db: Session, user_id: int):

    return db.query(models.Task).filter(models.Task.owner_id == user_id).all()


def get_task(db: Session, task_id: int):

    return db.query(models.Task).filter(models.Task.id == task_id).first()


def update_task(db: Session, task_id: int, task_data: schemas.TaskCreate):

    task = get_task(db, task_id)

    if task:
        task.title = task_data.title
        task.description = task_data.description
        task.priority = task_data.priority

        db.commit()
        db.refresh(task)

    return task


def delete_task(db: Session, task_id: int):

    task = get_task(db, task_id)

    if task:
        db.delete(task)
        db.commit()

    return task