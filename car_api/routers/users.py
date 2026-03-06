from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.core.database import get_session
from car_api.core.security import get_current_user, verify_user_permission
from car_api.models import User
from car_api.repositories.users import UserRepository
from car_api.schemas.users import (
    UserListPublicSchema,
    UserPublicSchema,
    UserSchema,
    UserUpdateSchema,
)
from car_api.services.users import UserService

user_routers = APIRouter(prefix="/api/users", tags=["Users"])


def get_user_repository(db: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository)


@user_routers.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublicSchema,
    summary="Criar um usuário",
)
async def create_user(
    user: UserSchema,
    user_service: UserService = Depends(get_user_service),
) -> UserPublicSchema:
    try:
        return await user_service.create_user(user)

    except HTTPException as http_ex:
        raise http_ex

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor",
        )


@user_routers.get(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublicSchema,
    summary="Selecionando um usuário específico",
)
async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> UserPublicSchema:
    try:
        return await user_service.get_user_by_id(user_id)

    except HTTPException as http_ex:
        raise http_ex

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor",
        )


@user_routers.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=UserListPublicSchema,
    summary="Listando usuários",
)
async def list_users(
    offset: int = Query(0, ge=0, description="Número de registros a serem pulados"),
    limit: int = Query(
        100, ge=1, le=100, description="Limite de registros a serem listados"
    ),
    search: Optional[str] = Query(None, description="Buscar por username ou email"),
    user_service: UserService = Depends(get_user_service),
) -> UserListPublicSchema:
    users = await user_service.list_users(offset, limit, search)

    return {"users": users, "offset": offset, "limit": limit}


@user_routers.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletando um usuário",
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.delete_user(user_id, current_user, verify_user_permission)

    except HTTPException as http_ex:
        raise http_ex

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor",
        )


@user_routers.put(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublicSchema,
    summary="Atualizando registro de usuário",
)
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserPublicSchema:
    update_data = user_data.model_dump(exclude_unset=True)

    new_user = await user_service.update_user(
        update_data, user_id, current_user, verify_user_permission
    )

    return new_user
