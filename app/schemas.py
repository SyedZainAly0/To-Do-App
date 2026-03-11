from pydantic import BaseModel, EmailStr
from typing import List, Optional

# ---------------- USER SCHEMAS ----------------

# This is the basic info about a user
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Info needed when creating a new user (signup)
class UserCreate(UserBase):
    password: str

# Info we send back after getting user data (response)
class UserResponse(UserBase):
    id: int                # user's ID in database
    is_active: bool        # is the account active?
    tasks: Optional[List["TaskResponse"]] = []  # list of tasks for this user

    class Config:
        orm_mode = True    # allows converting SQLAlchemy models to Pydantic easily

# ---------------- LOGIN SCHEMAS ----------------

# Info user sends to login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Info we send back after successful login
class LoginResponse(BaseModel):
    message: str
    access_token: str  # JWT token

# ---------------- TASK SCHEMAS ----------------

# Basic task info
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None  # optional field
    priority: Optional[int] = 1        # default priority is 1

# Info needed to create a task
class TaskCreate(TaskBase):
    pass  # same as TaskBase

# Info we send back after getting task data
class TaskResponse(TaskBase):
    id: int
    is_completed: bool
    owner_id: int   # which user owns this task

    class Config:
        orm_mode = True