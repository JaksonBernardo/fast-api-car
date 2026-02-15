from typing import Optional
from fastapi import APIRouter, status, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.models import User
from car_api.services.users import UserService
from car_api.core.database import get_session
from car_api.db import USERS
from car_api.schemas.users import (
    UserSchema,
    UserListPublicSchema,
    UserPublicSchema
)

user_routers = APIRouter(prefix="/api/users", tags=["Users"])

@user_routers.post(
    path = "/",
    status_code = status.HTTP_201_CREATED,
    response_model = UserPublicSchema,
    summary = "Criar um usuário"
)
async def create_user(
    user: UserSchema,
    db: AsyncSession = Depends(get_session)
) -> UserPublicSchema:

    try:

        return await UserService.create_user(db, user)
    
    except HTTPException as http_ex:

        raise http_ex

    except Exception as ex:

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Erro interno no servidor"
        )


@user_routers.get(
    path = "/{user_id}",
    status_code = status.HTTP_200_OK,
    response_model = UserPublicSchema,
    summary = "Selecionando um usuário específico"
)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_session),
) -> UserPublicSchema:
    
    try:

        return await UserService.get_user_by_id(db, user_id)

    except HTTPException as http_ex:

        raise http_ex

    except Exception as ex:

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Erro interno no servidor"
        )


@user_routers.delete(
    path = "/{user_id}",
    status_code = status.HTTP_204_NO_CONTENT,
    summary = "Deletando um usuário"
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_session)
):
    try:

        await UserService.delete_user(db, user_id)

    except HTTPException as http_ex:

        raise http_ex

    except Exception as ex:

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Erro interno no servidor"
        )


@user_routers.get(
    path = "/",
    status_code = status.HTTP_200_OK,
    response_model = UserListPublicSchema,
    summary = "Listando usuários"
)
async def list_users(
    offset: int = Query(0, ge = 0, description = "Número de registros a serem pulados"),
    limit: int = Query(100, ge = 1, le = 100, description = "Limite de registros a serem listados"),
    search: Optional[str] = Query(None, description = "Buscar por username ou email"),
    db: AsyncSession = Depends(get_session)
) -> UserListPublicSchema:
    
    users = await UserService.list_users(db, offset, limit, search)

    return {
        "users": users,
        "offset": offset,
        "limit": limit
    }




