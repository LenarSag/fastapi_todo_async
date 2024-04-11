from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, EmailStr


VALID_POSITIONS = ("guest", "user", "admin")


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserPosition(BaseModel):
    position: str

    @validator("position")
    def validate_position(cls, pos):
        if pos.lower() not in VALID_POSITIONS:
            raise ValueError("Position must be one of 'guest', 'user', or 'admin'")
        return pos.lower()


class UserDB(UserBase, UserPosition):
    id: int


class UserWithRelationships(UserDB):
    todos: Optional[list["TodoDB"]] = None


class UserAuth(BaseModel):
    id: int
    username: str
    position: str


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
