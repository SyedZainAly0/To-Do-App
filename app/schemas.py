from pydantic import BaseModel, EmailStr , Field
from typing import List, Optional




class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserResponse(UserBase):

    id: int
    is_active: bool
    tasks: Optional[List["TaskResponse"]] = []

    class Config:
        orm_mode = True




class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    access_token: str




class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[int] = 1


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):

    id: int
    is_completed: bool
    owner_id: int

    class Config:
        orm_mode = True