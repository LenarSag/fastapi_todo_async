from typing import Union
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from security.security import get_user_from_token
from db.schemas import UserDB, UserAuth, UserPosition, UserWithRelationships
from db.database import get_session
from db.crud import UserRepository


adminrouter = APIRouter()


def is_admin(auth_user: UserAuth):
    if auth_user.position.lower() == "admin":
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only admin is not allowed in this area!",
    )


@adminrouter.get("/")
async def get_admin_info(
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if is_admin(auth_user):
        return {"message": "Welcome, Admin!"}


@adminrouter.get("/users/", response_model=list[UserDB])
async def get_users(
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if is_admin(auth_user):
        users = await UserRepository.get_users(session)
        return users


@adminrouter.get("/users/{user_id}/", response_model=UserWithRelationships)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if is_admin(auth_user):
        user = await UserRepository.get_user_with_related(session, user_id)
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist"
        )


@adminrouter.put("/users/{user_id}/", response_model=dict[str, Union[UserDB, str]])
async def update_user_position(
    user_id: int,
    user_position: UserPosition = Depends(),
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if is_admin(auth_user):
        user = await UserRepository.get_user_by_id(session, user_id)
        if user:
            updated_user = await UserRepository.update_user_position(
                session, user, user_position
            )
            return {"user": updated_user, "message": "User updated successfully!"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@adminrouter.delete("/users/{user_id}/", response_model=dict[str, Union[UserDB, str]])
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if is_admin(auth_user):
        user = await UserRepository.get_user_with_related(session, user_id)
        if user:
            if user.position.lower() == "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can't delete admin user!",
                )
            result = await UserRepository.delete_user(session, user)
            if result:
                raise HTTPException(
                    status_code=status.HTTP_204_NO_CONTENT,
                    detail="User deleted successfully!",
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Couldn't delete user, try later",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
