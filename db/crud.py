from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from db import models, schemas


async def get_user(session: AsyncSession, username: str):
    query = select(models.User).filter_by(username=username)
    result = await session.execute(query)
    return result.scalars().first()


async def get_user_by_email(session: AsyncSession, email: str):
    query = select(models.User).filter_by(email=email)
    result = await session.execute(query)
    return result.scalars().first()


async def get_users(session: AsyncSession, skip: int = 0, limit: int = 10):
    query = select(models.User).offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


async def create_user(session: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_todo(session: AsyncSession, todo_id: int):
    query = select(models.Todo).filter_by(id=todo_id)
    db_todo = await session.execute(query)
    return db_todo.scalars().first()


async def get_todo_with_related(session: AsyncSession, todo_id: int):
    query = (
        select(models.Todo)
        .filter_by(id=todo_id)
        .options(joinedload(models.Todo.user), joinedload(models.Todo.category))
    )
    db_todo = await session.execute(query)
    return db_todo.scalars().first()


async def get_todos(session: AsyncSession):
    query = select(models.Todo)
    db_todos = await session.execute(query)
    return db_todos.scalars().all()


async def create_todo(session: AsyncSession, todo: schemas.TodoCreate, user_id: int):
    db_todo = models.Todo(
        user_id=user_id,
        text=todo.text,
        category_id=todo.category_id,
    )
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo


async def update_todo(
    session: AsyncSession, db_todo: models.Todo, new_todo_data: schemas.TodoCreate
):
    db_todo.text = new_todo_data.text
    db_todo.category_id = new_todo_data.category_id
    db_todo.completed = new_todo_data.completed
    await session.commit()
    await session.refresh(db_todo)
    return db_todo


async def delete_todo(session: AsyncSession, db_todo: models.Todo):
    await session.delete(db_todo)
    await session.commit()
    return True
