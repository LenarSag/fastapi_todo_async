from typing import Union

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from security.security import get_user_from_token
from db.database import get_session
from db.schemas import TodoCreate, TodoDB, TodoWithRelationships, UserAuth
from db.models import Todo
from db import crud


todosroute = APIRouter()


def user_can_read_create_todos(auth_user: UserAuth):
    if auth_user.position_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized"
        )
    return True


def user_can_edit_delete_todos(auth_user: UserAuth, todo: Todo):
    if auth_user.id != todo.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't update or delete this Todo! Only author or admin can do that!",
        )
    return True


@todosroute.get("/", response_model=list[TodoDB])
async def get_todos(
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if user_can_read_create_todos(auth_user):
        todos = await crud.get_todos(session)
        return todos


@todosroute.post("/", response_model=dict[str, Union[TodoDB, str]])
async def create_todo(
    todo_data: TodoCreate = Depends(),
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if user_can_read_create_todos(auth_user):
        todo = await crud.create_todo(session, todo_data, auth_user.id)
        return {"code": todo, "message": "Todo created successfully"}


@todosroute.get("/{todo_id}/", response_model=TodoWithRelationships)
async def get_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if user_can_read_create_todos(auth_user):
        todo = await crud.get_todo_with_related(session, todo_id)
        if todo:
            return todo
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found!"
        )


@todosroute.put("/{todo_id}/", response_model=TodoDB)
async def update_todo(
    todo_id: int,
    new_todo_data: TodoCreate = Depends(),
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    todo = await crud.get_todo(session, todo_id)
    if todo:
        user_can_edit_delete_todos(auth_user, todo)
        todo = await crud.update_todo(session, todo, new_todo_data)
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found!")


@todosroute.delete("/{todo_id}/")
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    todo = await crud.get_todo(session, todo_id)
    if todo:
        user_can_edit_delete_todos(auth_user, todo)
        result = await crud.delete_todo(session, todo)
        if result:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="Todo deleted successfully!",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Couldn't delete todo, try later",
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found!")
