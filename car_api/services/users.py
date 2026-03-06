from typing import Callable, Dict, Union

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.core.security import get_password_hash
from car_api.models import User
from car_api.repositories.users import UserRepository
from car_api.schemas.users import (
    UserListPublicSchema,
    UserPublicSchema,
    UserSchema,
)


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user: UserSchema) -> UserPublicSchema:
        username_exists = await self.user_repository.verify_if_exists_username(
            user.username
        )
        emails_exists = await self.user_repository.verify_if_exists_email(user.email)

        if username_exists or emails_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome ou email já está em uso",
            )

        hashed_password = get_password_hash(user.password)

        new_user = User(
            username=user.username, email=user.email, password=hashed_password
        )

        return await self.user_repository.save(new_user)

    async def delete_user(
        self,
        user_id: int,
        current_user: User,
        verify_user_permission: Callable,
    ) -> None:
        user_exists = await self.user_repository.verify_if_exists_id(user_id)

        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

        verify_user_permission(current_user, user_id)

        await self.user_repository.delete_by_id(user_id)

    async def get_user_by_id(self, user_id: int) -> UserPublicSchema | None:
        user_exists = await self.user_repository.verify_if_exists_id(user_id)

        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

        return await self.user_repository.get_user_by_id(user_id)

    async def list_users(
        self, offset: int, limit: int, search: Union[str, None]
    ) -> UserListPublicSchema:
        if search:
            search = f"%{search}%"

        users = await self.user_repository.get_users(offset, limit, search)

        return users

    async def update_user(
        self,
        user_data: Dict,
        user_id: int,
        current_user: User,
        verify_user_permission: Callable,
    ) -> UserPublicSchema:
        user_exists = await self.user_repository.verify_if_exists_id(user_id)

        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

        user = await self.user_repository.get_user_by_id(user_id)

        verify_user_permission(current_user, user_id)

        if "email" in user_data and user_data["email"] != user.email:
            email_exists = await self.user_repository.verify_if_exists_email(
                user_data["email"]
            )

            if email_exists:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Email indisponível"
                )

        if "password" in user_data:
            user_data["password"] = get_password_hash(user_data["password"])

        for field, value in user_data.items():
            setattr(user, field, value)

        new_user = await self.user_repository.update_user(user)

        return new_user
