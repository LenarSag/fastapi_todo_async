from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from db import models, schemas


class UserRepository:
    @classmethod
    async def get_user(cls, session: AsyncSession, username: str):
        query = select(models.User).filter_by(username=username)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_user_by_id(cls, session: AsyncSession, user_id: int):
        query = select(models.User).filter_by(id=user_id)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_user_with_related(cls, session: AsyncSession, user_id: int):
        query = (
            select(models.User)
            .filter_by(id=user_id)
            .options(joinedload(models.User.todos))
        )
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_user_by_email(cls, session: AsyncSession, email: str):
        query = select(models.User).filter_by(email=email)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_users(cls, session: AsyncSession, skip: int = 0, limit: int = 10):
        query = select(models.User).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def create_user(cls, session: AsyncSession, user: schemas.UserCreate):
        db_user = models.User(**user.model_dump())
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user

    @classmethod
    async def update_user_position(
        cls,
        session: AsyncSession,
        db_user: models.User,
        new_data: schemas.UserPosition,
    ):
        db_user.position = new_data.position
        await session.commit()
        await session.refresh(db_user)
        return db_user

    @classmethod
    async def delete_user(cls, session: AsyncSession, db_user: models.User):
        await session.delete(db_user)
        await session.commit()
        return True


class TodoRepository:
    @classmethod
    async def get_todo(cls, session: AsyncSession, todo_id: int):
        query = select(models.Todo).filter_by(id=todo_id)
        db_todo = await session.execute(query)
        return db_todo.scalars().first()

    @classmethod
    async def get_todo_with_related(cls, session: AsyncSession, todo_id: int):
        query = (
            select(models.Todo)
            .filter_by(id=todo_id)
            .options(joinedload(models.Todo.user), joinedload(models.Todo.category))
        )
        db_todo = await session.execute(query)
        return db_todo.scalars().first()

    @classmethod
    async def get_todos(cls, session: AsyncSession):
        query = select(models.Todo)
        db_todos = await session.execute(query)
        return db_todos.scalars().all()

    @classmethod
    async def create_todo(
        cls, session: AsyncSession, todo: schemas.TodoCreate, user_id: int
    ):
        db_todo = models.Todo(
            user_id=user_id,
            text=todo.text,
            category_id=todo.category_id,
        )
        session.add(db_todo)
        await session.commit()
        await session.refresh(db_todo)
        return db_todo

    @classmethod
    async def update_todo(
        cls,
        session: AsyncSession,
        db_todo: models.Todo,
        new_todo_data: schemas.TodoCreate,
    ):
        db_todo.text = new_todo_data.text
        db_todo.category_id = new_todo_data.category_id
        db_todo.completed = new_todo_data.completed
        await session.commit()
        await session.refresh(db_todo)
        return db_todo

    @classmethod
    async def delete_todo(cls, session: AsyncSession, db_todo: models.Todo):
        await session.delete(db_todo)
        await session.commit()
        return True
