from typing import Union

from fastapi import APIRouter, Response, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from security.security import get_user_from_token
from db.database import get_session
from db.schemas import CategoryCreate, CategoryDB, CategoryWithRelation, UserAuth
from db.crud import CategoryRepository
from routes.admin import is_admin


categoriesrouter = APIRouter()


def user_can_read_categories(auth_user: UserAuth):
    if auth_user.position.lower() == "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized"
        )
    return True


@categoriesrouter.get("/", response_model=list[CategoryDB])
async def get_categories(
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if user_can_read_categories(auth_user):
        categories = await CategoryRepository.get_categories(session)
        return categories


@categoriesrouter.post("/", response_model=dict[str, Union[CategoryDB, str]])
async def create_category(
    cat_data: CategoryCreate = Depends(),
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if is_admin(auth_user):
        category = await CategoryRepository.create_category(session, cat_data)
        return {"code": category, "message": "Category created successfully"}


@categoriesrouter.get("/{cat_id}/", response_model=CategoryWithRelation)
async def get_category(
    cat_id: int,
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    if user_can_read_categories(auth_user):
        category = await CategoryRepository.get_category_with_related(session, cat_id)
        if category:
            return category
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found!"
        )


@categoriesrouter.put("/{cat_id}/", response_model=CategoryDB)
async def update_category(
    cat_id: int,
    new_cat_data: CategoryCreate = Depends(),
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    category = await CategoryRepository.get_category(session, cat_id)
    if category:
        if is_admin(auth_user):
            category = await CategoryRepository.update_category(
                session, category, new_cat_data
            )
            return category
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Category not found!"
    )


@categoriesrouter.delete("/{cat_id}/")
async def delete_category(
    cat_id: int,
    session: AsyncSession = Depends(get_session),
    auth_user: UserAuth = Depends(get_user_from_token),
):
    category = await CategoryRepository.get_category(session, cat_id)
    if category:
        if is_admin(auth_user):
            result = await CategoryRepository.delete_category(session, category)
            if result:
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Couldn't delete category, try later",
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Category not found!"
    )
