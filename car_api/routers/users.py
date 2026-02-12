from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

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
