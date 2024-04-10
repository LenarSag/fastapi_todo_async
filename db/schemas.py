from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserDB(UserBase):
    id: int
    position_id: Optional[int] = None


class UserWithRelationships(UserDB):
    todos: Optional[list["TodoDB"]] = None
    position: Optional["PositionDB"] = None


class UserAuth(BaseModel):
    id: int
    username: str
    position_id: Optional[int] = None


class PositionCreate(BaseModel):
    position: str


class PositionDB(PositionCreate):
    id: int


class PositionWithRelationships(PositionDB):
    users: Optional[list["UserDB"]] = None


class TodoCreate(BaseModel):
    text: str
    category_id: Optional[int] = None
    completed: bool = False


class TodoDB(TodoCreate):
    id: int
    user_id: int
    created: datetime


class TodoWithRelationships(TodoDB):
    user: Optional["UserDB"] = None
    category: Optional["CategoryDB"] = None


class CategoryCreate(BaseModel):
    text: str
    slug: str


class CategoryDB(CategoryCreate):
    id: int


class CategoryWithRelationships(CategoryDB):
    todos: Optional[list["TodoDB"]] = None
